"""5-Phase Operational State Machine with S2 Deepening Loop, Guardrail Architecture, and Problem Graph Transitions.

Scientific Lineage & Attribution:
- TOTE Cybernetic Feedback Architecture: Miller, Galanter, & Pribram (1960)
- Well-Formed Outcome Sieve (P1..P6): Leslie Cameron-Bandler (1978) & Locke & Latham (2002)
- Multi-Agent Graph Workflow Design: Wang, Lin, & Irani (Google Cloud ADK 2 Workshop, 2026)
- 5-Phase Problem-Clarification Pipeline: Grounded in 02_map/five-phase-pipeline.md
"""

import re
from typing import Optional, Tuple, List, Dict
from .models import (
    StatePhase,
    PhaseAction,
    LLMTurnRecommendation,
    ProblemGraph,
    UtteranceNode,
    DetectionNode,
    QuestionNode,
    AnswerNode,
    SocraticIntent,
    OutcomePredicateKey,
    OutcomePredicateNode,
    PerspectiveNode,
    ConstraintNode,
    LayerType,
    GraphEdge,
)
from .classifier import (
    MetaModelClassifier,
    classify_domain,
    is_pragmatic_action,
)
from .socratic import (
    SocraticRouter,
    sanitize_domain_output,
    select_framing,
    is_tooling_or_build,
    is_infra_telemetry,
)
from .overlays import get_domain_pack
from ..config import DOMAIN_MAX_DEEPEN, DOMAIN_ECOLOGY_CAPS

CAPTURE_CUES = ("capture", "close this", "mark done", "that's enough", "capture this", "let's capture")

# Layer 1: Turn Budgets (Hard Caps per phase: min_turns, max_turns)
PHASE_TURN_BUDGETS: Dict[StatePhase, Tuple[int, int]] = {
    StatePhase.S0_IDLE: (0, 0),
    StatePhase.S1_INGEST: (0, 1),
    StatePhase.S2_CLARIFY: (1, 5),   # must ask at least 1, max 5 turns
    StatePhase.S3_OUTCOME: (1, 3),   # min 1, max 3 turns
    StatePhase.S4_ANGLE: (0, 2),     # skippable (min 0), max 2 turns
    StatePhase.S5_ECOLOGY: (1, 2),   # min 1, max 2 turns
    StatePhase.S6_DONE: (1, 1),      # exactly 1 synthesis turn
}

# Layer 2: Required Phase Gates (Non-skippable phases)
MANDATORY_PHASES = {
    StatePhase.S2_CLARIFY,
    StatePhase.S3_OUTCOME,
    StatePhase.S5_ECOLOGY,
    StatePhase.S6_DONE,
}

SESSION_HARD_MAX_TURNS = 15


def check_anti_spiral_brake(graph: ProblemGraph, current_phase: StatePhase) -> bool:
    """
    Layer 4: Anti-Spiral Brake.
    Detects if the conversation is stalling/looping within the current phase.
    Returns True if forced advance is required.
    """
    # Check user utterance semantic overlap across last 3 turns
    user_utts = [u.text for u in graph.utterances if u.speaker == "user"]
    if len(user_utts) >= 3:
        words_last = set(re.findall(r"\b\w{3,}\b", user_utts[-1].lower()))
        words_prev = set(re.findall(r"\b\w{3,}\b", user_utts[-2].lower()))
        words_prev2 = set(re.findall(r"\b\w{3,}\b", user_utts[-3].lower()))
        if words_last and words_prev and words_prev2:
            overlap1 = len(words_last & words_prev) / max(1, len(words_last | words_prev))
            overlap2 = len(words_last & words_prev2) / max(1, len(words_last | words_prev2))
            if overlap1 >= 0.60 and overlap2 >= 0.60:
                return True

    # Check intent repetition: 3 consecutive questions share exact same intent in current phase
    if len(graph.questions) >= 3:
        if (
            graph.questions[-1].socratic_intent == graph.questions[-2].socratic_intent == graph.questions[-3].socratic_intent
        ):
            turns = graph.phase_turn_counts.get(current_phase.value, 0)
            if turns >= 3:
                return True

    return False


class StateMachineEngine:
    """Manages phase transitions, detection priority queues, and the S2 deepening ladder with LLM veto guardrails."""

    def __init__(self, classifier: Optional[MetaModelClassifier] = None):
        self.classifier = classifier or MetaModelClassifier()

    def resolve_guardrail_action(
        self,
        graph: ProblemGraph,
        recommendation: Optional[LLMTurnRecommendation] = None,
    ) -> PhaseAction:
        """
        Evaluates the proposed phase action against the 6-layer guardrail architecture:
        1. Turn Budgets (Hard Caps)
        2. Required Phase Gates
        3. Anti-Spiral Brake
        4. Total Session Limit
        """
        current_phase = graph.current_phase
        turns_in_phase = graph.phase_turn_counts.get(current_phase.value, 0)
        total_user_turns = len([u for u in graph.utterances if u.speaker == "user"])

        # Hard session cap check
        if total_user_turns >= SESSION_HARD_MAX_TURNS and current_phase != StatePhase.S6_DONE:
            return PhaseAction.ADVANCE

        min_turns, max_turns = PHASE_TURN_BUDGETS.get(current_phase, (1, 5))

        # Deterministic default when no LLM recommendation is present
        if recommendation is None:
            if turns_in_phase >= max_turns:
                return PhaseAction.ADVANCE
            return PhaseAction.ADVANCE

        proposed = recommendation.phase_action

        # Layer 1: Turn Budget Veto
        if turns_in_phase >= max_turns:
            # Force advance if max turns reached (veto stay)
            effective = PhaseAction.ADVANCE
        elif turns_in_phase < min_turns and proposed in (PhaseAction.ADVANCE, PhaseAction.SKIP_NEXT):
            # Force stay if min turns not reached (veto premature advance)
            effective = PhaseAction.STAY
        else:
            effective = proposed

        # Layer 2: Required Phase Gates
        if effective == PhaseAction.SKIP_NEXT:
            # Only S4 (Angle) is skippable when transitioning from S3_OUTCOME
            if current_phase != StatePhase.S3_OUTCOME:
                effective = PhaseAction.ADVANCE

        # Layer 4: Anti-Spiral Brake
        if effective == PhaseAction.STAY and check_anti_spiral_brake(graph, current_phase):
            effective = PhaseAction.ADVANCE

        return effective

    def advance(
        self,
        graph: ProblemGraph,
        user_input: str,
        source_type: Optional[str] = None,
        llm_hint: Optional[str] = None,
        llm_conf: float = 0.0,
        llm_recommendation: Optional[LLMTurnRecommendation] = None,
    ) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """
        Processes a user turn through the state machine with guardrail veto rules.
        Returns: (new_phase, next_question_node, agent_response_text)
        """
        # Classify and track domain
        domain_res = classify_domain(
            user_input,
            prev_domain=graph.current_domain,
            domain_history=graph.domain_history,
            source_type=source_type,
            llm_hint=llm_hint,
            llm_conf=llm_conf,
        )
        graph.current_domain = domain_res.domain
        graph.blend_with = domain_res.blend_with
        graph.domain_history.append(domain_res.candidate)

        # Record user utterance
        utt = UtteranceNode(text=user_input, speaker="user")
        graph.utterances.append(utt)

        # Increment phase turn count & track history
        curr_phase_str = graph.current_phase.value
        graph.phase_turn_counts[curr_phase_str] = graph.phase_turn_counts.get(curr_phase_str, 0) + 1
        graph.phase_history.append(curr_phase_str)

        # Evaluate guardrails and determine effective action
        effective_action = self.resolve_guardrail_action(graph, llm_recommendation)

        # 1. State Phase Router
        if graph.current_phase == StatePhase.S0_IDLE:
            phase, q, resp = self._handle_s0_to_s1(graph, utt, llm_recommendation)

        elif graph.current_phase in (StatePhase.S1_INGEST, StatePhase.S2_CLARIFY):
            phase, q, resp = self._handle_s2_clarify(graph, utt, effective_action, llm_recommendation)

        elif graph.current_phase == StatePhase.S3_OUTCOME:
            phase, q, resp = self._handle_s3_outcome(graph, utt, effective_action, llm_recommendation)

        elif graph.current_phase == StatePhase.S4_ANGLE:
            phase, q, resp = self._handle_s4_angle(graph, utt, effective_action, llm_recommendation)

        elif graph.current_phase == StatePhase.S5_ECOLOGY:
            phase, q, resp = self._handle_s5_ecology(graph, utt, effective_action, llm_recommendation)

        elif graph.current_phase == StatePhase.S6_DONE:
            phase, q, resp = self._handle_s6_done(graph, utt, llm_recommendation)
        else:
            phase, q, resp = graph.current_phase, None, "Session concluded."

        # Layer 5: Domain boundary enforcement & sanitization
        sanitized_resp = sanitize_domain_output(resp, graph.current_domain)
        return phase, q, sanitized_resp

    def _handle_s0_to_s1(
        self,
        graph: ProblemGraph,
        utt: UtteranceNode,
        llm_recommendation: Optional[LLMTurnRecommendation] = None,
    ) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S0_IDLE -> S1_INGEST -> S2_CLARIFY"""
        graph.current_phase = StatePhase.S1_INGEST
        detections = self.classifier.classify(utt.text, utt.id, prev_domain=graph.current_domain)
        graph.detections.extend(detections)

        for det in detections:
            graph.edges.append(GraphEdge(source_id=utt.id, target_id=det.id, edge_type="utterance->detection"))

        # Check for dual-horizon upstream vs downstream link
        upstream_dets = [d for d in detections if d.layer == LayerType.UPSTREAM_STATE]
        downstream_dets = [d for d in detections if d.layer == LayerType.DOWNSTREAM_SYMPTOM]
        if upstream_dets and downstream_dets:
            graph.edges.append(
                GraphEdge(
                    source_id=upstream_dets[0].id,
                    target_id=downstream_dets[0].id,
                    edge_type="upstream->downstream",
                )
            )

        target_det = self.classifier.select_highest_priority(graph.detections)
        graph.current_phase = StatePhase.S2_CLARIFY

        if target_det:
            graph.active_detection_id = target_det.id
            q_node = SocraticRouter.route_base_question(target_det, domain=graph.current_domain, blend_with=graph.blend_with)
            graph.questions.append(q_node)
            graph.edges.append(GraphEdge(source_id=target_det.id, target_id=q_node.id, edge_type="detection->question"))

            ack = self._craft_acknowledgement(utt.text, target_det.layer, graph.current_domain)
            response_text = f"{ack}\n\n{q_node.framing_string}\n\n{q_node.text}"
            return StatePhase.S2_CLARIFY, q_node, response_text
        else:
            if is_pragmatic_action(utt.text):
                framing = "Let's check the pre-flight requirements and triggers before executing."
                if any(k in utt.text.lower() for k in ["phone", "battery", "monitor", "screen", "ram", "hardware"]):
                    q_text = "What specific symptoms, degradation, or device issues are prompting this repair or upgrade before you begin?"
                else:
                    q_text = "Before writing custom scripts or executing this plan, what underlying bottleneck or system trigger prompted this approach?"
            else:
                framing = select_framing(graph.current_domain, "open", blend_with=graph.blend_with)
                q_text = "What is the specific situation or decision that is creating the most friction right now?"
            q_node = QuestionNode(
                template_id="open_clarify_0",
                socratic_intent=SocraticIntent.CLARIFICATION,
                framing_string=framing,
                text=q_text,
                domain=graph.current_domain,
                blend_with=graph.blend_with,
            )
            graph.questions.append(q_node)
            ack = self._craft_acknowledgement(utt.text, LayerType.DOWNSTREAM_SYMPTOM, graph.current_domain)
            response_text = f"{ack}\n\n{framing}\n\n{q_text}"
            return StatePhase.S2_CLARIFY, q_node, response_text

    def _handle_s2_clarify(
        self,
        graph: ProblemGraph,
        utt: UtteranceNode,
        effective_action: PhaseAction = PhaseAction.ADVANCE,
        llm_recommendation: Optional[LLMTurnRecommendation] = None,
    ) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S2_CLARIFY: Evaluates answers against deepening protocol or moves to next detection / S3."""
        last_q = graph.questions[-1] if graph.questions else None
        target_det = next((d for d in graph.detections if d.id == graph.active_detection_id), None)

        # If in open clarification mode, ingest detections from detailed statement
        if not target_det and not any(not d.resolved for d in graph.detections):
            new_detections = self.classifier.classify(utt.text, utt.id, prev_domain=graph.current_domain)
            for new_d in new_detections:
                if not any(d.pattern == new_d.pattern and d.surface == new_d.surface for d in graph.detections):
                    graph.detections.append(new_d)
                    graph.edges.append(GraphEdge(source_id=utt.id, target_id=new_d.id, edge_type="utterance->detection"))

        is_closure = SocraticRouter.is_closure(utt.text)
        ans_node = AnswerNode(
            question_id=last_q.id if last_q else "none",
            text=utt.text,
            is_closure=is_closure,
            resolves_detection=False,
        )
        graph.answers.append(ans_node)
        if last_q:
            graph.edges.append(GraphEdge(source_id=last_q.id, target_id=ans_node.id, edge_type="question->answer"))

        # Early exit on capture cue in se/design domains
        user_lower = utt.text.lower()
        is_capture_cue = any(cue in user_lower for cue in CAPTURE_CUES)
        if is_capture_cue and graph.current_domain in ("se", "design"):
            if target_det:
                target_det.resolved = True
                target_det.resolved_by_answer_id = ans_node.id
                ans_node.resolves_detection = True
                graph.edges.append(GraphEdge(source_id=ans_node.id, target_id=target_det.id, edge_type="answer->resolution"))
            for d in graph.detections:
                d.resolved = True
            graph.current_phase = StatePhase.S3_OUTCOME
            graph.active_detection_id = None
            return self._init_s3_outcome(graph, llm_recommendation)

        # If LLM recommended advancing and guardrails approved
        if effective_action == PhaseAction.ADVANCE and llm_recommendation is not None:
            if target_det:
                target_det.resolved = True
                target_det.resolved_by_answer_id = ans_node.id
                ans_node.resolves_detection = True
            for d in graph.detections:
                d.resolved = True
            graph.current_phase = StatePhase.S3_OUTCOME
            graph.active_detection_id = None
            return self._init_s3_outcome(graph, llm_recommendation)

        # Deepening Check (domain-aware cycles on closure)
        max_cycles = DOMAIN_MAX_DEEPEN.get(graph.current_domain, 2)
        if target_det and is_closure and target_det.deepen_count < max_cycles:
            target_det.deepen_count += 1
            deepen_q = SocraticRouter.route_deepening_question(
                target_det, target_det.deepen_count, utt.text, domain=graph.current_domain, blend_with=graph.blend_with
            )
            graph.questions.append(deepen_q)
            graph.edges.append(GraphEdge(source_id=target_det.id, target_id=deepen_q.id, edge_type="detection->question"))

            if graph.current_domain == "se":
                ack = "We landed on that quickly. Let's trace the underlying service data."
            elif graph.current_domain == "design":
                ack = "We landed on that quickly. Let's check the user interaction evidence."
            else:
                ack = "We landed on that very quickly, which makes total sense given how often this plays out."
            response_text = f"{ack}\n\n{deepen_q.framing_string}\n\n{deepen_q.text}"
            return StatePhase.S2_CLARIFY, deepen_q, response_text

        # If not closure OR reached max cycles -> Resolve this detection
        if target_det:
            target_det.resolved = True
            target_det.resolved_by_answer_id = ans_node.id
            ans_node.resolves_detection = True
            graph.edges.append(GraphEdge(source_id=ans_node.id, target_id=target_det.id, edge_type="answer->resolution"))
            graph.active_detection_id = None

        # Find next unresolved detection in priority order
        next_det = self.classifier.select_highest_priority(graph.detections)
        if next_det:
            graph.active_detection_id = next_det.id
            next_q = SocraticRouter.route_base_question(next_det, domain=graph.current_domain, blend_with=graph.blend_with)
            graph.questions.append(next_q)
            graph.edges.append(GraphEdge(source_id=next_det.id, target_id=next_q.id, edge_type="detection->question"))

            ack = "Understood. That gives us a much clearer picture of that layer."
            response_text = f"{ack}\n\n{next_q.framing_string}\n\n{next_q.text}"
            return StatePhase.S2_CLARIFY, next_q, response_text

        # If LLM recommended staying and guardrails approved STAY
        if effective_action == PhaseAction.STAY and llm_recommendation is not None:
            framing = select_framing(graph.current_domain, SocraticIntent.CLARIFICATION, blend_with=graph.blend_with)
            q_text = "What specific factors, symptoms, or system triggers seem to drive this pattern?"
            q_node = QuestionNode(
                template_id="s2_deepen_stay",
                socratic_intent=llm_recommendation.socratic_intent if llm_recommendation else SocraticIntent.CLARIFICATION,
                framing_string=framing,
                text=q_text,
                domain=graph.current_domain,
                blend_with=graph.blend_with,
            )
            graph.questions.append(q_node)
            return StatePhase.S2_CLARIFY, q_node, f"{framing}\n\n{q_text}"

        # All detections clarified and ready to advance -> Transition to S3_OUTCOME
        graph.current_phase = StatePhase.S3_OUTCOME
        graph.active_detection_id = None
        return self._init_s3_outcome(graph, llm_recommendation)

    def _init_s3_outcome(
        self,
        graph: ProblemGraph,
        llm_recommendation: Optional[LLMTurnRecommendation] = None,
    ) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """Initializes S3 Outcome Architecture (Well-Formed Outcomes)."""
        wfo_keys = [
            OutcomePredicateKey.POSITIVE,
            OutcomePredicateKey.SELF_INITIATED,
            OutcomePredicateKey.SENSORY,
            OutcomePredicateKey.CHUNK,
            OutcomePredicateKey.ECOLOGY,
        ]
        for key in wfo_keys:
            if key not in graph.outcome_predicates:
                graph.outcome_predicates[key] = OutcomePredicateNode(key=key, status="missing")

        # Ask first WFO predicate (Positive state)
        framing = select_framing(graph.current_domain, SocraticIntent.PROBE_ALTERNATIVE, blend_with=graph.blend_with)
        all_text = " ".join(u.text.lower() for u in graph.utterances)
        if graph.current_domain == "se" and is_tooling_or_build(all_text):
            q_text = "Stated in the positive — what specific capability or workflow do you want the final software or tool to deliver?"
        else:
            q_text = "Stated in the positive — what do you actually want to achieve, rather than what you're trying to avoid?"
        q_node = QuestionNode(
            template_id="wfo_positive_1",
            socratic_intent=SocraticIntent.PROBE_ALTERNATIVE,
            framing_string=framing,
            text=q_text,
            domain=graph.current_domain,
            blend_with=graph.blend_with,
        )
        graph.questions.append(q_node)
        response_text = f"We have reached the bedrock of the problem.\n\n{framing}\n\n{q_text}"
        return StatePhase.S3_OUTCOME, q_node, response_text

    def _handle_s3_outcome(
        self,
        graph: ProblemGraph,
        utt: UtteranceNode,
        effective_action: PhaseAction = PhaseAction.ADVANCE,
        llm_recommendation: Optional[LLMTurnRecommendation] = None,
    ) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S3_OUTCOME: Populates WFO predicates and drives to S4_ANGLE or S5_ECOLOGY (if skipping S4)."""
        pos_node = graph.outcome_predicates.get(OutcomePredicateKey.POSITIVE)
        self_node = graph.outcome_predicates.get(OutcomePredicateKey.SELF_INITIATED)
        sens_node = graph.outcome_predicates.get(OutcomePredicateKey.SENSORY)

        # If LLM recommended skipping S4 (Angle) and guardrails approved
        if effective_action == PhaseAction.SKIP_NEXT:
            if pos_node and pos_node.status == "missing":
                pos_node.statement = utt.text
                pos_node.status = "drafted"
            elif self_node and self_node.status == "missing":
                self_node.statement = utt.text
                self_node.status = "drafted"
            elif sens_node and sens_node.status == "missing":
                sens_node.statement = utt.text
                sens_node.status = "drafted"
            return self._init_s5_ecology(graph, llm_recommendation)

        # If LLM recommended advance and we're ready
        if effective_action == PhaseAction.ADVANCE and llm_recommendation is not None:
            if pos_node and pos_node.status == "missing":
                pos_node.statement = utt.text
                pos_node.status = "drafted"
            elif self_node and self_node.status == "missing":
                self_node.statement = utt.text
                self_node.status = "drafted"
            elif sens_node and sens_node.status == "missing":
                sens_node.statement = utt.text
                sens_node.status = "drafted"
            return self._init_s4_angle(graph, llm_recommendation)

        if pos_node and pos_node.status == "missing":
            pos_node.statement = utt.text
            pos_node.status = "drafted"
            framing = select_framing(graph.current_domain, SocraticIntent.PROBE_CAUSAL_LINK, blend_with=graph.blend_with)
            q_text = "Is this outcome within your 100% direct control to initiate and maintain, or does it depend on someone else's action?"
            q_node = QuestionNode(
                template_id="wfo_self_initiated_1",
                socratic_intent=SocraticIntent.PROBE_CAUSAL_LINK,
                framing_string=framing,
                text=q_text,
                domain=graph.current_domain,
                blend_with=graph.blend_with,
            )
            graph.questions.append(q_node)
            return StatePhase.S3_OUTCOME, q_node, f"Got it.\n\n{framing}\n\n{q_text}"

        elif self_node and self_node.status == "missing":
            self_node.statement = utt.text
            self_node.status = "drafted"
            framing = select_framing(graph.current_domain, SocraticIntent.PROBE_EVIDENCE, blend_with=graph.blend_with)
            if graph.current_domain == "se":
                all_text = " ".join(u.text.lower() for u in graph.utterances)
                if is_infra_telemetry(all_text):
                    q_text = "What specific, observable telemetry metric will tell you this is resolved — what will the dashboard, p95 panel, or error log show?"
                else:
                    q_text = "What specific, observable output or verification (such as batch throughput, exported files, or error-free execution) will tell you this is working?"
            elif graph.current_domain == "design":
                q_text = "What specific, observable user behavior will tell you this is resolved — what will the task completion rate or click path show?"
            else:
                q_text = "What specific, observable evidence will tell you that you've achieved this — what will you literally see, hear, or measure?"
            q_node = QuestionNode(
                template_id="wfo_sensory_1",
                socratic_intent=SocraticIntent.PROBE_EVIDENCE,
                framing_string=framing,
                text=q_text,
                domain=graph.current_domain,
                blend_with=graph.blend_with,
            )
            graph.questions.append(q_node)
            return StatePhase.S3_OUTCOME, q_node, f"Clear.\n\n{framing}\n\n{q_text}"

        elif sens_node and sens_node.status == "missing":
            sens_node.statement = utt.text
            sens_node.status = "drafted"
            return self._init_s4_angle(graph, llm_recommendation)

        return self._init_s4_angle(graph, llm_recommendation)

    def _init_s4_angle(
        self,
        graph: ProblemGraph,
        llm_recommendation: Optional[LLMTurnRecommendation] = None,
    ) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S4_ANGLE: Generate 1st/2nd/3rd/Systemic perspectives + Reframe grounded in active domain."""
        graph.current_phase = StatePhase.S4_ANGLE
        pack = get_domain_pack(graph.current_domain)
        p_dict = pack.s4_perspectives
        pos_1_title, pos_1_content = p_dict.get("1st", ("Direct Perspective", "Operating from your core objectives."))
        pos_2_title, pos_2_content = p_dict.get("2nd", ("Counterparty Angle", "Seeing constraints and external pressures."))
        pos_3_title, pos_3_content = p_dict.get("3rd", ("Objective Observer", "Evaluating only verifiable data and metrics."))
        ref_title, ref_content = p_dict.get("reframe", ("Systemic Reframe", "Treating the challenge as a structural constraint."))

        graph.perspectives = [
            PerspectiveNode(position="1st", title=pos_1_title, content=pos_1_content),
            PerspectiveNode(position="2nd", title=pos_2_title, content=pos_2_content),
            PerspectiveNode(position="3rd", title=pos_3_title, content=pos_3_content),
            PerspectiveNode(position="reframe", title=ref_title, content=ref_content),
        ]

        if graph.current_domain == "se":
            all_text = " ".join(u.text.lower() for u in graph.utterances)
            if is_infra_telemetry(all_text):
                framing = "Let's inspect this from black-box telemetry and caller perspectives."
                q_text = "Looking at this from the 3rd-position (the telemetry traces and service dashboards) — what does the data show that we might have overlooked?"
            else:
                framing = "Let's inspect this from an objective engineering perspective."
                q_text = "Looking at this from the 3rd-position (an objective engineer reviewing the toolchain and hardware constraints) — what trade-offs or alternatives might we have overlooked?"
        elif graph.current_domain == "design":
            framing = "Let's inspect this from the first-time user perspective."
            q_text = "Looking at this from the 3rd-position (the raw session replay of the user) — what does the click path show that we might have overlooked?"
        elif graph.current_domain == "leadership":
            framing = "Let's inspect this from multiple organizational perspectives."
            q_text = "Looking at this from the 3rd-position (a neutral third-party reviewing written commitments) — what does that observer see that we might have overlooked?"
        else:
            framing = "Let's test this from multiple objective viewpoints."
            q_text = "Looking at this from the 3rd-position (an objective observer who only saw the data) — what does that observer see that you might have missed?"

        q_node = QuestionNode(
            template_id="angle_perspective_1",
            socratic_intent=SocraticIntent.PROBE_VIEWPOINT,
            framing_string=framing,
            text=q_text,
            domain=graph.current_domain,
        )
        graph.questions.append(q_node)
        resp = f"We have structured the outcome predicates. Now let's explore alternative angles.\n\n{framing}\n\n{q_text}"
        return StatePhase.S4_ANGLE, q_node, resp

    def _handle_s4_angle(
        self,
        graph: ProblemGraph,
        utt: UtteranceNode,
        effective_action: PhaseAction = PhaseAction.ADVANCE,
        llm_recommendation: Optional[LLMTurnRecommendation] = None,
    ) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S4_ANGLE: Explores angle or advances to S5_ECOLOGY. Pivots on disengagement."""
        # Disengagement pivot: user is stuck on abstract framing, offer concrete re-entry
        if SocraticRouter.is_disengaged(utt.text):
            if graph.current_domain == "se":
                pivot_q = "Let's come at this differently — when this system WAS running smoothly, what was different about that setup or configuration?"
            elif graph.current_domain == "design":
                pivot_q = "Let's come at this differently — think of a time a user completed this flow without friction. What was different about that session?"
            elif graph.current_domain == "leadership":
                pivot_q = "Let's come at this differently — was there a time this stakeholder dynamic worked well? What was different then?"
            else:
                pivot_q = "That question might not land right now — and that's fine. Let's come at this differently. When things ARE going well for you, what's different about those moments?"
            q_node = QuestionNode(
                template_id="angle_disengage_pivot",
                socratic_intent=SocraticIntent.PROBE_ALTERNATIVE,
                framing_string="Pivoting to concrete experience.",
                text=pivot_q,
                domain=graph.current_domain,
            )
            graph.questions.append(q_node)
            return StatePhase.S4_ANGLE, q_node, pivot_q

        if effective_action == PhaseAction.STAY:
            pack = get_domain_pack(graph.current_domain)
            p_dict = pack.s4_perspectives
            ref_title, ref_content = p_dict.get("reframe", ("Systemic Reframe", "Treating the challenge as a structural constraint."))
            framing = "Let's explore the systemic reframe angle."
            q_text = f"If we view this from a systemic reframe ({ref_title}) — what new leverage point becomes visible?"
            q_node = QuestionNode(
                template_id="angle_reframe_2",
                socratic_intent=SocraticIntent.PROBE_VIEWPOINT,
                framing_string=framing,
                text=q_text,
                domain=graph.current_domain,
            )
            graph.questions.append(q_node)
            return StatePhase.S4_ANGLE, q_node, f"Understood on that observer angle.\n\n{framing}\n\n{q_text}"

        return self._init_s5_ecology(graph, llm_recommendation)

    def _init_s5_ecology(
        self,
        graph: ProblemGraph,
        llm_recommendation: Optional[LLMTurnRecommendation] = None,
    ) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S5_ECOLOGY: Stress-test systemic costs and trade-offs."""
        graph.current_phase = StatePhase.S5_ECOLOGY
        if graph.current_domain == "se":
            all_text = " ".join(u.text.lower() for u in graph.utterances)
            if is_infra_telemetry(all_text):
                framing = "Now we stress-test operational failover and system trade-offs."
                q_text = "If we deploy this solution tomorrow, what is the trade-off in latency, resource utilization, or operational complexity?"
            else:
                framing = "Now we stress-test development maintenance and operational trade-offs."
                q_text = "If you adopt or build this solution tomorrow, what is the trade-off in ongoing maintenance time, setup complexity, or toolchain dependencies?"
        elif graph.current_domain == "design":
            framing = "Now we stress-test user journey trade-offs."
            q_text = "If we ship this flow tomorrow, what is the trade-off in user cognitive load or edge-case flows?"
        elif graph.current_domain == "leadership":
            framing = "Now we stress-test stakeholder ecology and trade-offs."
            q_text = "If you execute this decision tomorrow, what is the cost or trade-off in team bandwidth or stakeholder alignment?"
        else:
            framing = "Now we stress-test the ecology and trade-offs."
            q_text = "If you achieve this exact outcome tomorrow, what is the cost or trade-off? What do you have to give up or renegotiate?"

        q_node = QuestionNode(
            template_id="ecology_check_1",
            socratic_intent=SocraticIntent.PROBE_IMPLICATION,
            framing_string=framing,
            text=q_text,
            domain=graph.current_domain,
        )
        graph.questions.append(q_node)
        return StatePhase.S5_ECOLOGY, q_node, f"That perspective adds valuable clarity.\n\n{framing}\n\n{q_text}"

    def _handle_s5_ecology(
        self,
        graph: ProblemGraph,
        utt: UtteranceNode,
        effective_action: PhaseAction = PhaseAction.ADVANCE,
        llm_recommendation: Optional[LLMTurnRecommendation] = None,
    ) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S5_ECOLOGY -> S6_DONE: Final synthesis. Pivots on disengagement."""
        # Disengagement pivot: user stuck on abstract trade-off, offer concrete version
        if SocraticRouter.is_disengaged(utt.text):
            graph.s5_disengagement_count += 1

            # One-strike rule: second disengagement in S5 -> bail to S6_DONE
            if graph.s5_disengagement_count >= 2:
                graph.current_phase = StatePhase.S6_DONE
                return self._handle_s6_done(graph, utt, llm_recommendation)

            # First disengagement: pivot to a concrete version of the question
            if graph.current_domain == "se":
                pivot_q = "Let's make this concrete — if you ship this fix tomorrow, what is the very first thing that could go wrong in production?"
            elif graph.current_domain == "design":
                pivot_q = "Let's make this concrete — if you push this flow live tomorrow, what's the first edge case a real user would hit?"
            elif graph.current_domain == "leadership":
                pivot_q = "Let's make this concrete — if you announce this decision tomorrow morning, who pushes back first and what do they say?"
            else:
                pivot_q = "Let's make this concrete — if you woke up tomorrow with this fully resolved, what's the very first thing that would be different about your day?"
            q_node = QuestionNode(
                template_id="ecology_disengage_pivot",
                socratic_intent=SocraticIntent.PROBE_IMPLICATION,
                framing_string="Pivoting to concrete next-step.",
                text=pivot_q,
                domain=graph.current_domain,
            )
            graph.questions.append(q_node)
            return StatePhase.S5_ECOLOGY, q_node, pivot_q

        graph.constraints.append(
            ConstraintNode(
                text=utt.text,
                severity="medium",
                positive_intent="Protecting focus and sustainable execution.",
            )
        )
        user_lower = utt.text.lower()
        is_capture_cue = any(cue in user_lower for cue in CAPTURE_CUES)

        max_ecology = DOMAIN_ECOLOGY_CAPS.get(graph.current_domain, 1)

        if llm_recommendation is not None:
            if effective_action == PhaseAction.ADVANCE or is_capture_cue or len(graph.constraints) >= max_ecology:
                graph.current_phase = StatePhase.S6_DONE
                return self._handle_s6_done(graph, utt, llm_recommendation)
        else:
            if len(graph.constraints) >= max_ecology or is_capture_cue:
                graph.current_phase = StatePhase.S6_DONE
                return self._handle_s6_done(graph, utt, llm_recommendation)

        if len(graph.constraints) < max_ecology:
            framing = "Now let's check secondary stakeholder and organizational bandwidth."
            q_text = "What is the secondary trade-off in team bandwidth or stakeholder alignment if you execute this?"
            q_node = QuestionNode(
                template_id="ecology_check_2",
                socratic_intent=SocraticIntent.PROBE_IMPLICATION,
                framing_string=framing,
                text=q_text,
                domain=graph.current_domain,
            )
            graph.questions.append(q_node)
            return StatePhase.S5_ECOLOGY, q_node, f"That trade-off is recorded.\n\n{framing}\n\n{q_text}"

        graph.current_phase = StatePhase.S6_DONE
        return self._handle_s6_done(graph, utt, llm_recommendation)

    def _handle_s6_done(
        self,
        graph: ProblemGraph,
        utt: UtteranceNode,
        llm_recommendation: Optional[LLMTurnRecommendation] = None,
    ) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S6_DONE: Synthesizes Problem Graph into a completed Decision Record."""
        # Graceful close: if ADR was already delivered, return short ack
        s6_turns = graph.phase_turn_counts.get(StatePhase.S6_DONE.value, 0)
        if s6_turns > 1:
            return StatePhase.S6_DONE, None, (
                "Session complete. Your Problem Record is above — "
                "revisit it anytime you need to recalibrate."
            )

        pos = graph.outcome_predicates.get(OutcomePredicateKey.POSITIVE)
        sens = graph.outcome_predicates.get(OutcomePredicateKey.SENSORY)

        pack = get_domain_pack(graph.current_domain)
        summary = (
            f"### {pack.artifact_title} — Problem Deconstructed & Bedrock Reached\n\n"
            f"- **Clarified Outcome:** {pos.statement if pos else 'Actionable, self-directed execution plan.'}\n"
            f"- **Sensory Evidence:** {sens.statement if sens else 'Measurable feedback indicators verified.'}\n"
            f"- **Resolved Distortions:** {len([d for d in graph.detections if d.resolved])} cognitive layers peeled back.\n"
            f"- **Systemic Constraints:** {len(graph.constraints)} trade-offs mapped and protected.\n\n"
            "Here's the bedrock this was sitting on — and the outcome that follows from it. You own this outcome fully."
        )
        return StatePhase.S6_DONE, None, summary

    def _craft_acknowledgement(self, text: str, layer: LayerType, domain: str = "general") -> str:
        """Crafts an empathic acknowledgment without endorsing distortions, tailored to domain."""
        dom = domain.lower() if domain else "general"
        if dom == "se":
            if layer == LayerType.UPSTREAM_STATE:
                return "Acknowledged on the sustained system pressure and on-call load."
            if is_tooling_or_build(text):
                return "Understood on the build-versus-buy trade-off and batch workflow requirements."
            return "Acknowledged on the service constraint and operational friction."
        elif dom == "design":
            if layer == LayerType.UPSTREAM_STATE:
                return "I hear the creative fatigue and design block."
            return "I see the user friction and journey breakdown."
        elif dom == "leadership":
            if layer == LayerType.UPSTREAM_STATE:
                return "That is a heavy leadership load to carry when organizational reserves are thin."
            return "Understood on the stakeholder alignment tension."
        else:
            if layer == LayerType.UPSTREAM_STATE:
                return "That sounds like a heavy load to carry, especially when energy and reserves are already stretched thin."
            if is_pragmatic_action(text):
                return "Understood on the practical goal and execution plan."
            return "Understood on the situation and where things stand."
