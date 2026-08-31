"""Unit tests for the 5-Phase State Machine."""

import pytest
from thinking_partner.agent.state_machine import StateMachineEngine
from thinking_partner.agent.models import ProblemGraph, StatePhase, PatternType, OutcomePredicateKey


def test_state_machine_initialization_and_s2():
    engine = StateMachineEngine()
    graph = ProblemGraph()

    # Turn 1: User brings problem
    phase, q, resp = engine.advance(graph, "They don't think I'm leadership material because I'm quiet.")
    assert phase == StatePhase.S2_CLARIFY
    assert len(graph.detections) >= 1
    assert q is not None
    assert q.deepen_cycle == 0


def test_state_machine_s2_deepening_closure():
    engine = StateMachineEngine()
    graph = ProblemGraph()

    # Step 1: Input problem
    engine.advance(graph, "They don't think I'm leadership material.")
    target_det_id = graph.active_detection_id
    det = next(d for d in graph.detections if d.id == target_det_id)

    # Step 2: User provides shallow closure -> enters Deepening Cycle 1
    phase, q, resp = engine.advance(graph, "that's the only thing")
    assert phase == StatePhase.S2_CLARIFY
    assert det.deepen_count == 1
    assert q.deepen_cycle == 1
    assert not det.resolved

    # Step 3: User provides second closure -> enters Deepening Cycle 2
    phase, q, resp = engine.advance(graph, "I don't know")
    assert phase == StatePhase.S2_CLARIFY
    assert det.deepen_count == 2
    assert q.deepen_cycle == 2
    assert not det.resolved

    # Step 4: Concrete answer supplied -> resolves detection
    phase, q, resp = engine.advance(graph, "In the meeting yesterday, the VP asked who wanted to lead the project and didn't look at me.")
    assert det.resolved is True


def test_state_machine_full_pipeline_progression():
    engine = StateMachineEngine()
    graph = ProblemGraph()

    # S1 -> S2 (Ingest problem)
    engine.advance(graph, "They don't think I am capable of leading the project.")
    assert graph.current_phase == StatePhase.S2_CLARIFY

    # Resolve detection -> transitions to S3_OUTCOME
    engine.advance(graph, "The director told me yesterday that I should focus on IC tasks instead.")
    assert graph.current_phase == StatePhase.S3_OUTCOME

    # S3: Supply positive goal -> verifies POSITIVE predicate
    engine.advance(graph, "I want to present the technical roadmap directly to the executive committee next quarter.")
    assert OutcomePredicateKey.POSITIVE in graph.outcome_predicates

    # S3: Supply self-initiated check -> verifies SELF_INITIATED predicate
    engine.advance(graph, "Yes, by defining the milestone schedule myself.")
    assert OutcomePredicateKey.SELF_INITIATED in graph.outcome_predicates

    # S3: Supply sensory evidence check -> verifies SENSORY predicate & transitions to S4_ANGLE
    engine.advance(graph, "The director formally signs off on the sprint backlog.")
    assert graph.current_phase == StatePhase.S4_ANGLE

    # S4 -> S5
    engine.advance(graph, "From the executive perspective, they want de-risked delivery with clear milestone metrics.")
    assert graph.current_phase == StatePhase.S5_ECOLOGY

    # S5: Add constraint 1 (leadership has 2 ecology checks)
    engine.advance(graph, "The only trade-off is 5 hours a week away from pure coding, which is completely acceptable.")
    assert graph.current_phase == StatePhase.S5_ECOLOGY

    # S5: Add constraint 2 & finalize to S6_DONE
    engine.advance(graph, "The secondary trade-off is shifting 10% sprint bandwidth to documentation. Let's capture this.")
    assert graph.current_phase == StatePhase.S6_DONE


def test_wfo_five_predicates_keys():
    # Check all 5 OutcomePredicateKey values exist
    keys = [
        OutcomePredicateKey.POSITIVE,
        OutcomePredicateKey.SELF_INITIATED,
        OutcomePredicateKey.SENSORY,
        OutcomePredicateKey.CHUNK,
        OutcomePredicateKey.ECOLOGY,
    ]
    assert len(keys) == 5


def test_state_machine_open_clarify_to_multi_distortion_resolution():
    """
    Tests open clarification start followed by multi-distortion intake and resolution:
    Turn 1 (general statement -> 0 detections): enters S2_CLARIFY with open_clarify_0
    Turn 2 (user provides distortions): ingests cause_effect, universal_quantifier, comparative_deletion
    Turns 3..: resolves detections sequentially and advances to S3_OUTCOME.
    """
    engine = StateMachineEngine()
    graph = ProblemGraph()

    # Turn 1: Open clarification prompt
    phase1, q1, resp1 = engine.advance(graph, "We have a performance situation in production.")
    assert phase1 == StatePhase.S2_CLARIFY
    assert q1.template_id == "open_clarify_0"

    # Turn 2: User provides detailed distortions
    phase2, q2, resp2 = engine.advance(
        graph, "Every time we add replicas it gets worse, it's just the database."
    )
    assert phase2 == StatePhase.S2_CLARIFY
    assert len(graph.detections) >= 2
    assert any(d.pattern == PatternType.CAUSE_EFFECT for d in graph.detections)
    assert any(d.pattern == PatternType.UNIVERSAL_QUANTIFIER for d in graph.detections)

    # Turn 3: Resolve active detection with concrete answer
    active_det = next(d for d in graph.detections if d.id == graph.active_detection_id)
    phase3, q3, resp3 = engine.advance(
        graph, "When we profiled during load test, connection pool saturated at 50 max connections."
    )
    assert active_det.resolved is True


def test_guardrail_turn_budget_max_veto():
    """
    Layer 1: Verifies that if LLM tries to stay beyond max turn budget in S2 (5 turns),
    the state machine vetoes the stay and force-advances to S3_OUTCOME on the 6th turn.
    """
    from thinking_partner.agent.models import LLMTurnRecommendation, PhaseAction, SocraticIntent
    engine = StateMachineEngine()
    graph = ProblemGraph()

    # Ingest problem (Turn 1 -> S2)
    engine.advance(graph, "My service is timing out randomly.")
    assert graph.current_phase == StatePhase.S2_CLARIFY

    inputs = [
        "We observed latency spike in redis cache.",
        "The postgres connection pool is exhausted.",
        "Worker threads blocked on network io calls.",
        "Garbage collection pauses reached two seconds.",
    ]
    intents = [
        SocraticIntent.PROBE_CAUSAL_LINK,
        SocraticIntent.PROBE_EVIDENCE,
        SocraticIntent.PROBE_ASSUMPTION,
        SocraticIntent.PROBE_CONCEPT,
    ]

    # Turns 2 to 5 in S2 with diverse content and intents
    for inp, intent in zip(inputs, intents):
        stay_rec = LLMTurnRecommendation(
            response_text="Exploring this subsystem.",
            socratic_intent=intent,
            phase_action=PhaseAction.STAY,
            phase_reason="Exploring root cause",
        )
        phase, _, _ = engine.advance(graph, inp, llm_recommendation=stay_rec)
        assert phase == StatePhase.S2_CLARIFY

    # On Turn 6 in S2 (hitting max 5 turns in S2), state machine MUST veto stay and force advance to S3
    stay_rec = LLMTurnRecommendation(
        response_text="Let's dig deeper into that.",
        socratic_intent=SocraticIntent.CLARIFICATION,
        phase_action=PhaseAction.STAY,
        phase_reason="Still trying to stay",
    )
    phase, _, _ = engine.advance(graph, "Operating system page faults increasing rapidly.", llm_recommendation=stay_rec)
    assert phase == StatePhase.S3_OUTCOME
    assert graph.current_phase == StatePhase.S3_OUTCOME


def test_guardrail_skip_s4_angle_allowed():
    """
    Layer 2: Verifies that LLM CAN recommend skip_next for S4_ANGLE when in S3_OUTCOME,
    and state machine advances directly to S5_ECOLOGY.
    """
    from thinking_partner.agent.models import LLMTurnRecommendation, PhaseAction, SocraticIntent
    engine = StateMachineEngine()
    graph = ProblemGraph()

    # Move to S3
    engine.advance(graph, "We have database contention on checkout.")
    advance_rec = LLMTurnRecommendation(
        response_text="Root cause identified.",
        socratic_intent=SocraticIntent.PROBE_EVIDENCE,
        phase_action=PhaseAction.ADVANCE,
    )
    engine.advance(graph, "The lock contention is on inventory row.", llm_recommendation=advance_rec)
    assert graph.current_phase == StatePhase.S3_OUTCOME

    # In S3, LLM recommends skip_next (skipping S4 angle)
    skip_rec = LLMTurnRecommendation(
        response_text="Perspective shift is unnecessary here, moving to trade-offs.",
        socratic_intent=SocraticIntent.PROBE_IMPLICATION,
        phase_action=PhaseAction.SKIP_NEXT,
    )
    phase, _, _ = engine.advance(graph, "I want zero checkout timeouts.", llm_recommendation=skip_rec)
    assert phase == StatePhase.S5_ECOLOGY
    assert graph.current_phase == StatePhase.S5_ECOLOGY


def test_guardrail_mandatory_gate_vetoes_illegal_skip():
    """
    Layer 2: Verifies that LLM CANNOT skip mandatory phases like S2 or S5.
    If LLM requests skip_next in S2, state machine vetoes skip and treats it as advance to S3.
    """
    from thinking_partner.agent.models import LLMTurnRecommendation, PhaseAction, SocraticIntent
    engine = StateMachineEngine()
    graph = ProblemGraph()

    engine.advance(graph, "My build is failing.")
    assert graph.current_phase == StatePhase.S2_CLARIFY

    illegal_skip_rec = LLMTurnRecommendation(
        response_text="Skipping straight ahead.",
        socratic_intent=SocraticIntent.CLARIFICATION,
        phase_action=PhaseAction.SKIP_NEXT,
    )
    # Attempt illegal skip in S2 -> should advance to S3 (not skip S3!)
    phase, _, _ = engine.advance(graph, "The compiler threw syntax error.", llm_recommendation=illegal_skip_rec)
    assert phase == StatePhase.S3_OUTCOME
    assert graph.current_phase == StatePhase.S3_OUTCOME


def test_guardrail_anti_spiral_brake():
    """
    Layer 4: Anti-Spiral Brake.
    Verifies that if user answers repeat identically (>60% word overlap over 3 turns)
    while LLM recommends stay, the brake triggers on the 3rd turn and forces an advance out of S2.
    """
    from thinking_partner.agent.models import LLMTurnRecommendation, PhaseAction, SocraticIntent
    engine = StateMachineEngine()
    graph = ProblemGraph()

    # Turn 1: Ingest problem
    engine.advance(graph, "Database queries are running slow during peak traffic.")
    assert graph.current_phase == StatePhase.S2_CLARIFY

    stay_rec = LLMTurnRecommendation(
        response_text="Can you say more about that?",
        socratic_intent=SocraticIntent.PROBE_CAUSAL_LINK,
        phase_action=PhaseAction.STAY,
    )

    # Turn 2: Repetitive answer
    phase2, _, _ = engine.advance(graph, "Queries are running slow during peak traffic load.", llm_recommendation=stay_rec)
    assert phase2 == StatePhase.S2_CLARIFY

    # Turn 3: 3rd repetitive answer (>60% word overlap across all 3 turns) -> anti-spiral brake triggers advance
    phase3, _, _ = engine.advance(graph, "Queries are running slow during peak traffic load every day.", llm_recommendation=stay_rec)
    assert phase3 == StatePhase.S3_OUTCOME
    assert graph.current_phase == StatePhase.S3_OUTCOME


def test_disengagement_detector():
    """Verifies the disengagement detector catches stuck/confused signals."""
    from thinking_partner.agent.socratic import SocraticRouter

    # Clear disengagement signals
    assert SocraticRouter.is_disengaged("idk") is True
    assert SocraticRouter.is_disengaged("i don't know") is True
    assert SocraticRouter.is_disengaged("idk? i have a thought and i cant sleep? idk how an observer would view that") is True
    assert SocraticRouter.is_disengaged("no idea") is True
    assert SocraticRouter.is_disengaged("i'm not sure what you mean") is True
    assert SocraticRouter.is_disengaged("how would i know that") is True
    assert SocraticRouter.is_disengaged("as i said idk") is True

    # NOT disengagement (substantive answers)
    assert SocraticRouter.is_disengaged("The director told me to focus on IC tasks.") is False
    assert SocraticRouter.is_disengaged("I want to present the roadmap to the exec committee.") is False
    assert SocraticRouter.is_disengaged("Yes, by defining the milestone schedule myself.") is False


def test_s4_disengagement_pivot():
    """
    Session-log failure: user says 'idk' to 3rd-position observer question in S4.
    System should pivot to concrete experiential question, NOT advance to S5.
    """
    engine = StateMachineEngine()
    graph = ProblemGraph()

    # Advance to S4_ANGLE through the pipeline
    engine.advance(graph, "They don't think I'm capable of leading.")
    engine.advance(graph, "The director told me to focus on IC work instead.")  # -> S3
    engine.advance(graph, "I want to present the roadmap to the exec committee.")  # positive
    engine.advance(graph, "Yes, by defining the milestone schedule myself.")  # self-initiated
    engine.advance(graph, "The director formally signs off on the sprint backlog.")  # sensory -> S4
    assert graph.current_phase == StatePhase.S4_ANGLE

    # User disengages on abstract 3rd-position question
    phase, q, resp = engine.advance(graph, "idk? i dont know how an observer would see that")
    assert phase == StatePhase.S4_ANGLE, "Should stay in S4, not advance to S5"
    assert q is not None
    assert q.template_id == "angle_disengage_pivot"
    assert "differently" in resp.lower()


def test_s5_disengagement_pivot():
    """
    Session-log failure: user says 'idk' to ecology trade-off question in S5.
    System should pivot to concrete version, NOT march straight to S6_DONE.
    """
    engine = StateMachineEngine()
    graph = ProblemGraph()

    # Advance to S5_ECOLOGY
    engine.advance(graph, "i keep waking up and cant fall back to sleep")
    engine.advance(graph, "if i cant sleep my day becomes very sluggish, i cant work properly")  # -> S3
    engine.advance(graph, "have enough energy to do what i need to do everyday")  # positive
    engine.advance(graph, "yes and no, there are nights i just cant fall asleep")  # self-initiated
    engine.advance(graph, "well sometimes i get ideas i cant stop thinking about")  # sensory -> S4
    engine.advance(graph, "I see that stress patterns disrupt my sleep.")  # S4 -> S5
    assert graph.current_phase == StatePhase.S5_ECOLOGY

    # User disengages on abstract trade-off question
    phase, q, resp = engine.advance(graph, "as i said idk")
    assert phase == StatePhase.S5_ECOLOGY, "Should stay in S5, not advance to S6"
    assert q is not None
    assert q.template_id == "ecology_disengage_pivot"
    assert "concrete" in resp.lower()
