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

    # S5: Add constraint & finalize to S6_DONE
    engine.advance(graph, "The only trade-off is 5 hours a week away from pure coding, which is completely acceptable.")
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
