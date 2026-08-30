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
    OutcomePredicateKey,
    OutcomePredicateNode,
    PerspectiveNode,
    ConstraintNode,
    LayerType,
    GraphEdge,
)
from .classifier import MetaModelClassifier
from .socratic import SocraticRouter


class StateMachineEngine:
    """Manages phase transitions, detection priority queues, and the S2 deepening ladder."""

    def __init__(self, classifier: Optional[MetaModelClassifier] = None):
        self.classifier = classifier or MetaModelClassifier()

    def advance(self, graph: ProblemGraph, user_input: str) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """
        Processes a user turn through the state machine.
        Returns: (new_phase, next_question_node, agent_response_text)
        """
        # Record user utterance
        utt = UtteranceNode(text=user_input, speaker="user")
        graph.utterances.append(utt)

        # 1. State Phase Router
        if graph.current_phase == StatePhase.S0_IDLE:
            return self._handle_s0_to_s1(graph, utt)

        elif graph.current_phase in (StatePhase.S1_INGEST, StatePhase.S2_CLARIFY):
            return self._handle_s2_clarify(graph, utt)

        elif graph.current_phase == StatePhase.S3_OUTCOME:
            return self._handle_s3_outcome(graph, utt)

        elif graph.current_phase == StatePhase.S4_ANGLE:
            return self._handle_s4_angle(graph, utt)

        elif graph.current_phase == StatePhase.S5_ECOLOGY:
            return self._handle_s5_ecology(graph, utt)

        elif graph.current_phase == StatePhase.S6_DONE:
            return self._handle_s6_done(graph, utt)

        return graph.current_phase, None, "Session concluded."

    def _handle_s0_to_s1(self, graph: ProblemGraph, utt: UtteranceNode) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S0_IDLE -> S1_INGEST -> S2_CLARIFY"""
        graph.current_phase = StatePhase.S1_INGEST
        detections = self.classifier.classify(utt.text, utt.id)
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
            q_node = SocraticRouter.route_base_question(target_det)
            graph.questions.append(q_node)
            graph.edges.append(GraphEdge(source_id=target_det.id, target_id=q_node.id, edge_type="detection->question"))
            
            # Format turn: Acknowledgement + Framing + Socratic Question
            ack = self._craft_acknowledgement(utt.text, target_det.layer)
            response_text = f"{ack}\n\n{q_node.framing_string}\n\n{q_node.text}"
            return StatePhase.S2_CLARIFY, q_node, response_text
        else:
            # No specific pattern matched: open clarification
            framing = "Problems stack — each one rests on an assumption beneath it. Let's descend together to the load-bearing one."
            q_text = "What is the specific situation or decision that is creating the most friction right now?"
            q_node = QuestionNode(
                template_id="open_clarify_0",
                socratic_intent=SocraticRouter.route_base_question(
                    DetectionNode(utterance_id=utt.id, pattern="simple_deletion", surface="friction", span=[0, 0])
                ).socratic_intent,
                framing_string=framing,
                text=q_text,
            )
            graph.questions.append(q_node)
            response_text = f"I hear you. Let's make sure we ground this clearly.\n\n{framing}\n\n{q_text}"
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
                target_det, target_det.deepen_count, utt.text
            )
            graph.questions.append(deepen_q)
            graph.edges.append(GraphEdge(source_id=target_det.id, target_id=deepen_q.id, edge_type="detection->question"))

            # Deepening voice rule: acknowledge fast closure with curiosity
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
            next_q = SocraticRouter.route_base_question(next_det)
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
        framing = "Now that we've reached the bedrock assumption, let's architect the outcome."
        q_text = "Stated in the positive — what do you actually want to achieve, rather than what you're trying to avoid?"
        q_node = QuestionNode(
            template_id="wfo_positive_1",
            socratic_intent=SocraticRouter.route_base_question(
                DetectionNode(utterance_id="none", pattern="modal_necessity", surface="want", span=[0, 0])
            ).socratic_intent,
            framing_string=framing,
            text=q_text,
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
            framing = "Let's check who owns the control."
            q_text = "Is this outcome within your 100% direct control to initiate and maintain, or does it depend on someone else's action?"
            q_node = QuestionNode(
                template_id="wfo_self_initiated_1",
                socratic_intent=SocraticRouter.route_base_question(
                    DetectionNode(utterance_id="none", pattern="cause_effect", surface="control", span=[0, 0])
                ).socratic_intent,
                framing_string=framing,
                text=q_text,
            )
            graph.questions.append(q_node)
            return StatePhase.S3_OUTCOME, q_node, f"Got it.\n\n{framing}\n\n{q_text}"

        elif self_node and self_node.status == "missing":
            self_node.statement = utt.text
            self_node.status = "drafted"
            # Ask Sensory Evidence predicate
            framing = "Let's define the observable milestone."
            q_text = "What specific, observable evidence will tell you that you've achieved this — what will you literally see, hear, or measure?"
            q_node = QuestionNode(
                template_id="wfo_sensory_1",
                socratic_intent=SocraticRouter.route_base_question(
                    DetectionNode(utterance_id="none", pattern="mind_reading", surface="evidence", span=[0, 0])
                ).socratic_intent,
                framing_string=framing,
                text=q_text,
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
        """S4_ANGLE: Generate 1st/2nd/3rd/Systemic perspectives + Reframe."""
        graph.perspectives = [
            PerspectiveNode(
                position="1st",
                title="Your Direct Perspective",
                content="Operating from your core objectives with direct agency and realistic boundaries.",
            ),
            PerspectiveNode(
                position="2nd",
                title="Counterparty / Stakeholder Angle",
                content="Seeing the interaction from their operational constraints, deadlines, and unstated pressures.",
            ),
            PerspectiveNode(
                position="3rd",
                title="Objective Observer (Fly on the Wall)",
                content="Viewing the dynamic without emotional charge — evaluating only the verifiable facts and structural incentives.",
            ),
            PerspectiveNode(
                position="reframe",
                title="Cognitive Reframe",
                content="Treating the perceived limitation not as an identity deficit, but as a lack of calibrated feedback mechanisms.",
            ),
        ]

        framing = "Let's test this from multiple psychological distances."
        q_text = "Looking at this from the 3rd-position (an objective observer who only saw the data) — what does that observer see that you might have filtered out?"
        q_node = QuestionNode(
            template_id="angle_perspective_1",
            socratic_intent=SocraticRouter.route_base_question(
                DetectionNode(utterance_id="none", pattern="unspecified_referent", surface="observer", span=[0, 0])
            ).socratic_intent,
            framing_string=framing,
            text=q_text,
        )
        graph.questions.append(q_node)
        resp = "We have structured the outcome predicates. Now let's explore alternative angles.\n\n" + framing + "\n\n" + q_text
        return StatePhase.S4_ANGLE, q_node, resp

    def _handle_s4_angle(self, graph: ProblemGraph, utt: UtteranceNode) -> Tuple[StatePhase, Optional[QuestionNode], str]:
        """S4_ANGLE -> S5_ECOLOGY: Stress-test systemic costs."""
        graph.current_phase = StatePhase.S5_ECOLOGY
        framing = "Now we stress-test the ecology and trade-offs."
        q_text = "If you achieve this exact outcome tomorrow, what is the cost or trade-off? What do you have to give up or renegotiate?"
        q_node = QuestionNode(
            template_id="ecology_check_1",
            socratic_intent=SocraticRouter.route_base_question(
                DetectionNode(utterance_id="none", pattern="cause_effect", surface="trade-off", span=[0, 0])
            ).socratic_intent,
            framing_string=framing,
            text=q_text,
        )
        graph.questions.append(q_node)
        return StatePhase.S5_ECOLOGY, q_node, f"That perspective adds valuable distance.\n\n{framing}\n\n{q_text}"

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

        summary = (
            "### Problem Deconstructed & Bedrock Reached\n\n"
            f"- **Clarified Outcome:** {pos.statement if pos else 'Actionable, self-directed execution plan.'}\n"
            f"- **Sensory Evidence:** {sens.statement if sens else 'Measurable feedback indicators verified.'}\n"
            f"- **Resolved Distortions:** {len([d for d in graph.detections if d.resolved])} cognitive layers peeled back.\n"
            f"- **Systemic Constraints:** {len(graph.constraints)} trade-offs mapped and protected.\n\n"
            "Here's the bedrock this was sitting on — and the outcome that follows from it. You own this outcome fully."
        )
        return StatePhase.S6_DONE, None, summary

    def _craft_acknowledgement(self, text: str, layer: LayerType) -> str:
        """Crafts an empathic acknowledgment without endorsing distortions."""
        if layer == LayerType.UPSTREAM_STATE:
            return "That sounds like a heavy load to carry, especially when energy and reserves are already stretched thin."
        return "That sounds like a real weight to carry. I hear the tension in that."
