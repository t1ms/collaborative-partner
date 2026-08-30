"""5-Phase Operational State Machine with S2 Deepening Loop and Problem Graph Transitions.

Scientific Lineage & Attribution:
- TOTE Cybernetic Feedback Architecture: Miller, Galanter, & Pribram (1960)
- Well-Formed Outcome Sieve (P1..P6): Leslie Cameron-Bandler (1978) & Locke & Latham (2002)
- Multi-Agent Graph Workflow Design: Wang, Lin, & Irani (Google Cloud ADK 2 Workshop, 2026)
- 5-Phase Problem-Clarification Pipeline: Grounded in 02_map/five-phase-pipeline.md
"""

from typing import Optional, Tuple, List, Dict
from .models import (
    StatePhase,
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
from .classifier import MetaModelClassifier, classify_domain
from .socratic import SocraticRouter, sanitize_domain_output, select_framing
from .overlays import get_domain_pack


class StateMachineEngine:
    """Manages phase transitions, detection priority queues, and the S2 deepening ladder."""

    def __init__(self, classifier: Optional[MetaModelClassifier] = None):
        self.classifier = classifier or MetaModelClassifier()

    def advance(self, graph: ProblemGraph, user_input: str, source_type: Optional[str] = None) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """
        Processes a user turn through the state machine.
        Returns: (new_phase, next_question_node, agent_response_text)
        """
        # Classify and track domain
        domain_res = classify_domain(
            user_input,
            prev_domain=graph.current_domain,
            domain_history=graph.domain_history,
            source_type=source_type,
        )
        graph.current_domain = domain_res.domain
        graph.blend_with = domain_res.blend_with
        graph.domain_history.append(domain_res.candidate)

        # Record user utterance
        utt = UtteranceNode(text=user_input, speaker="user")
        graph.utterances.append(utt)

        # 1. State Phase Router
        if graph.current_phase == StatePhase.S0_IDLE:
            phase, q, resp = self._handle_s0_to_s1(graph, utt)

        elif graph.current_phase in (StatePhase.S1_INGEST, StatePhase.S2_CLARIFY):
            phase, q, resp = self._handle_s2_clarify(graph, utt)

        elif graph.current_phase == StatePhase.S3_OUTCOME:
            phase, q, resp = self._handle_s3_outcome(graph, utt)

        elif graph.current_phase == StatePhase.S4_ANGLE:
            phase, q, resp = self._handle_s4_angle(graph, utt)

        elif graph.current_phase == StatePhase.S5_ECOLOGY:
            phase, q, resp = self._handle_s5_ecology(graph, utt)

        elif graph.current_phase == StatePhase.S6_DONE:
            phase, q, resp = self._handle_s6_done(graph, utt)
        else:
            phase, q, resp = graph.current_phase, None, "Session concluded."

        # Sanitize final deterministic response
        sanitized_resp = sanitize_domain_output(resp, graph.current_domain)
        return phase, q, sanitized_resp

    def _handle_s0_to_s1(self, graph: ProblemGraph, utt: UtteranceNode) -> Tuple[StatePhase, Optional[QuestionNode], str]:
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
            
            # Format turn: Acknowledgement + Framing + Socratic Question
            ack = self._craft_acknowledgement(utt.text, target_det.layer, graph.current_domain)
            response_text = f"{ack}\n\n{q_node.framing_string}\n\n{q_node.text}"
            return StatePhase.S2_CLARIFY, q_node, response_text
        else:
            # No specific pattern matched: open clarification
            framing = select_framing(graph.current_domain, "open", blend_with=graph.blend_with)
            q_text = "What is the specific situation or decision that is creating the most friction right now?"
            q_node = QuestionNode(
                template_id="open_clarify_0",
                socratic_intent=SocraticRouter.route_base_question(
                    DetectionNode(utterance_id=utt.id, pattern="simple_deletion", surface="friction", span=[0, 0]),
                    domain=graph.current_domain,
                    blend_with=graph.blend_with,
                ).socratic_intent,
                framing_string=framing,
                text=q_text,
                domain=graph.current_domain,
                blend_with=graph.blend_with,
            )
            graph.questions.append(q_node)
            ack = self._craft_acknowledgement(utt.text, LayerType.DOWNSTREAM_SYMPTOM, graph.current_domain)
            response_text = f"{ack}\n\n{framing}\n\n{q_text}"
            return StatePhase.S2_CLARIFY, q_node, response_text

    def _handle_s2_clarify(self, graph: ProblemGraph, utt: UtteranceNode) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S2_CLARIFY: Evaluates answers against deepening protocol or moves to next detection / S3."""
        # Find the last asked question
        last_q = graph.questions[-1] if graph.questions else None
        target_det = next((d for d in graph.detections if d.id == graph.active_detection_id), None)

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

        # Deepening Check (max 2 extra cycles on closure)
        if target_det and is_closure and target_det.deepen_count < 2:
            target_det.deepen_count += 1
            deepen_q = SocraticRouter.route_deepening_question(
                target_det, target_det.deepen_count, utt.text, domain=graph.current_domain, blend_with=graph.blend_with
            )
            graph.questions.append(deepen_q)
            graph.edges.append(GraphEdge(source_id=target_det.id, target_id=deepen_q.id, edge_type="detection->question"))

            # Deepening voice rule: acknowledge fast closure with curiosity
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

        # All detections clarified! Transition to S3_OUTCOME
        graph.current_phase = StatePhase.S3_OUTCOME
        graph.active_detection_id = None
        return self._init_s3_outcome(graph)

    def _init_s3_outcome(self, graph: ProblemGraph) -> Tuple[StatePhase, Optional[QuestionNode], str]:
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
        q_text = "Stated in the positive — what do you actually want to achieve, rather than what you're trying to avoid?"
        q_node = QuestionNode(
            template_id="wfo_positive_1",
            socratic_intent=SocraticRouter.route_base_question(
                DetectionNode(utterance_id="none", pattern="modal_necessity", surface="want", span=[0, 0]),
                domain=graph.current_domain,
                blend_with=graph.blend_with,
            ).socratic_intent,
            framing_string=framing,
            text=q_text,
            domain=graph.current_domain,
            blend_with=graph.blend_with,
        )
        graph.questions.append(q_node)
        response_text = f"We have reached the bedrock of the problem.\n\n{framing}\n\n{q_text}"
        return StatePhase.S3_OUTCOME, q_node, response_text

    def _handle_s3_outcome(self, graph: ProblemGraph, utt: UtteranceNode) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S3_OUTCOME: Populates WFO predicates and drives to S4_ANGLE."""
        # Find the first unfulfilled predicate
        pos_node = graph.outcome_predicates.get(OutcomePredicateKey.POSITIVE)
        self_node = graph.outcome_predicates.get(OutcomePredicateKey.SELF_INITIATED)
        sens_node = graph.outcome_predicates.get(OutcomePredicateKey.SENSORY)

        if pos_node and pos_node.status == "missing":
            pos_node.statement = utt.text
            pos_node.status = "drafted"
            # Ask Self-Initiated predicate
            framing = select_framing(graph.current_domain, SocraticIntent.PROBE_CAUSAL_LINK, blend_with=graph.blend_with)
            q_text = "Is this outcome within your 100% direct control to initiate and maintain, or does it depend on someone else's action?"
            q_node = QuestionNode(
                template_id="wfo_self_initiated_1",
                socratic_intent=SocraticRouter.route_base_question(
                    DetectionNode(utterance_id="none", pattern="cause_effect", surface="control", span=[0, 0]),
                    domain=graph.current_domain,
                    blend_with=graph.blend_with,
                ).socratic_intent,
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
            # Ask Sensory Evidence predicate
            framing = select_framing(graph.current_domain, SocraticIntent.PROBE_EVIDENCE, blend_with=graph.blend_with)
            if graph.current_domain == "se":
                q_text = "What specific, observable telemetry metric will tell you this is resolved — what will the dashboard, p95 panel, or error log show?"
            elif graph.current_domain == "design":
                q_text = "What specific, observable user behavior will tell you this is resolved — what will the task completion rate or click path show?"
            else:
                q_text = "What specific, observable evidence will tell you that you've achieved this — what will you literally see, hear, or measure?"
            q_node = QuestionNode(
                template_id="wfo_sensory_1",
                socratic_intent=SocraticRouter.route_base_question(
                    DetectionNode(utterance_id="none", pattern="mind_reading", surface="evidence", span=[0, 0]),
                    domain=graph.current_domain,
                    blend_with=graph.blend_with,
                ).socratic_intent,
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
            # Mark all as drafted and move to S4
            graph.current_phase = StatePhase.S4_ANGLE
            return self._init_s4_angle(graph)

        graph.current_phase = StatePhase.S4_ANGLE
        return self._init_s4_angle(graph)

    def _init_s4_angle(self, graph: ProblemGraph) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S4_ANGLE: Generate 1st/2nd/3rd/Systemic perspectives + Reframe grounded in active domain."""
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
            framing = "Let's inspect this from black-box telemetry and caller perspectives."
            q_text = "Looking at this from the 3rd-position (the telemetry traces and service dashboards) — what does the data show that we might have overlooked?"
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
            socratic_intent=SocraticRouter.route_base_question(
                DetectionNode(utterance_id="none", pattern="unspecified_referent", surface="observer", span=[0, 0]),
                domain=graph.current_domain,
            ).socratic_intent,
            framing_string=framing,
            text=q_text,
            domain=graph.current_domain,
        )
        graph.questions.append(q_node)
        resp = f"We have structured the outcome predicates. Now let's explore alternative angles.\n\n{framing}\n\n{q_text}"
        return StatePhase.S4_ANGLE, q_node, resp

    def _handle_s4_angle(self, graph: ProblemGraph, utt: UtteranceNode) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S4_ANGLE -> S5_ECOLOGY: Stress-test systemic costs."""
        graph.current_phase = StatePhase.S5_ECOLOGY
        if graph.current_domain == "se":
            framing = "Now we stress-test operational failover and system trade-offs."
            q_text = "If we deploy this solution tomorrow, what is the trade-off in latency, resource utilization, or operational complexity?"
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
            socratic_intent=SocraticRouter.route_base_question(
                DetectionNode(utterance_id="none", pattern="cause_effect", surface="trade-off", span=[0, 0]),
                domain=graph.current_domain,
            ).socratic_intent,
            framing_string=framing,
            text=q_text,
            domain=graph.current_domain,
        )
        graph.questions.append(q_node)
        return StatePhase.S5_ECOLOGY, q_node, f"That perspective adds valuable clarity.\n\n{framing}\n\n{q_text}"

    def _handle_s5_ecology(self, graph: ProblemGraph, utt: UtteranceNode) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S5_ECOLOGY -> S6_DONE: Final synthesis."""
        graph.constraints.append(
            ConstraintNode(
                text=utt.text,
                severity="medium",
                positive_intent="Protecting focus and sustainable execution.",
            )
        )
        graph.current_phase = StatePhase.S6_DONE
        return self._handle_s6_done(graph, utt)

    def _handle_s6_done(self, graph: ProblemGraph, utt: UtteranceNode) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S6_DONE: Synthesizes Problem Graph into a completed Decision Record."""
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
            return "That sounds like a real weight to carry. I hear the tension in that."
