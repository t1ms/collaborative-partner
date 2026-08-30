"""Unit tests for domain grounding, hysteresis, 1-turn cross-domain blending, and forbidden string isolation."""

import pytest
from thinking_partner.agent.orchestrator import ThinkingPartnerOrchestrator
from thinking_partner.agent.models import ProblemGraph, StatePhase
from thinking_partner.agent.classifier import classify_domain


def test_domain_fluid_blend_se_leadership_se():
    """
    Test Case 1:
    Turn 1 (SE): "Our checkout p95 is 900ms at 3x load on the payment service." -> locks to 'se'
    Turn 2 (SE): "The queue depth spikes on Grafana whenever PagerDuty alerts fire." -> stays 'se'
    Turn 3 (Leadership jump): "and product keeps pinging the team asking for roadmap updates."
           -> stays 'se' with blend_with='leadership' (1-turn blend)
    Turn 4 (SE): "The database replica is hitting CPU saturation during the load test."
           -> returns cleanly to 'se' with blend_with=None
    """
    orchestrator = ThinkingPartnerOrchestrator()
    graph = ProblemGraph()

    # Turn 1: SE
    resp1, graph, art1 = orchestrator.process_turn(
        graph, "Our checkout p95 is 900ms at 3x load on the payment service."
    )
    assert graph.current_domain == "se"
    assert graph.blend_with is None
    assert art1 is not None
    assert "ADR" in art1.title or "Architecture" in art1.title

    # Turn 2: SE
    resp2, graph, art2 = orchestrator.process_turn(
        graph, "The queue depth spikes on Grafana whenever PagerDuty alerts fire."
    )
    assert graph.current_domain == "se"
    assert graph.blend_with is None

    # Turn 3: Single-turn jump to Leadership
    resp3, graph, art3 = orchestrator.process_turn(
        graph, "and product keeps pinging the team asking for roadmap updates."
    )
    # Hysteresis rule: stays SE, but sets blend_with='leadership'
    assert graph.current_domain == "se"
    assert graph.blend_with == "leadership"
    assert any(k in resp3.lower() for k in ["product", "stakeholder", "telemetry", "queue", "roadmap"])

    # Turn 4: Back to SE
    resp4, graph, art4 = orchestrator.process_turn(
        graph, "The database replica is hitting CPU saturation during the load test."
    )
    # Returns cleanly to SE
    assert graph.current_domain == "se"
    assert graph.blend_with is None


def test_domain_hard_transition_se_to_design():
    """
    Test Case 2:
    Turn 1: SE statement -> locks to 'se'
    Turn 2: First Design hit -> stays 'se' with blend_with='design'
    Turn 3: Second consecutive Design hit -> confirmed hard transition to 'design', blend_with=None
    """
    orchestrator = ThinkingPartnerOrchestrator()
    graph = ProblemGraph()

    # Turn 1: SE
    orchestrator.process_turn(graph, "Our checkout p95 is 900ms at 3x load.")
    assert graph.current_domain == "se"

    # Turn 2: 1st Design hit
    orchestrator.process_turn(graph, "Users bounce at onboarding because the prototype empty state is confusing.")
    assert graph.current_domain == "se"
    assert graph.blend_with == "design"

    # Turn 3: 2nd consecutive Design hit -> confirmed switch!
    resp3, graph, art3 = orchestrator.process_turn(
        graph, "The click path shows massive drop-off right on the Figma mockup flow."
    )
    assert graph.current_domain == "design"
    assert graph.blend_with is None
    assert "Journey" in art3.title or "Canvas" in art3.title


def test_forbidden_strings_absent_in_se_and_design():
    """
    Test Case 3:
    Ensures forbidden phrases ('psychological distance', 'filtering out', etc.)
    never leak into SE or Design conversations/traces.
    """
    orchestrator = ThinkingPartnerOrchestrator()
    graph = ProblemGraph()

    # Full progression through SE domain
    turns = [
        "Our checkout p95 latency is 900ms at 3x load and PagerDuty alerts constantly fire.",
        "that's the only thing",
        "The trace waterfall shows Redis locks timing out under load.",
        "I want to maintain sub-200ms p95 latency across all replicas under 5x load.",
        "Yes, by configuring connection pooling and read replicas myself.",
        "Grafana dashboards show p95 stays below 200ms with zero 5xx alerts.",
        "From downstream callers, they only see contract SLA compliance.",
        "The trade-off is 15% higher infrastructure memory footprint.",
    ]

    for turn in turns:
        resp, graph, art = orchestrator.process_turn(graph, turn)
        # Check forbidden phrases in response
        assert "psychological distance" not in resp.lower()
        assert "filtering out" not in resp.lower()
        assert "metacognitive" not in resp.lower()

    # Verify graph perspectives and artifacts also do not contain forbidden strings
    for p in graph.perspectives:
        assert "psychological distance" not in p.title.lower()
        assert "psychological distance" not in p.content.lower()


def test_cold_start_immediate_lock():
    """
    Test Case 4:
    Turn 1 starting from 'general' with strong keywords locks immediately to target domain.
    """
    res_se = classify_domain("Our checkout p95 is 900ms on the payment service API with PagerDuty alerts.", prev_domain="general")
    assert res_se.domain == "se"
    assert res_se.blend_with is None
    assert res_se.confidence >= 0.60

    res_design = classify_domain("Users bounce at onboarding because the Figma prototype empty state causes drop-off.", prev_domain="general")
    assert res_design.domain == "design"
    assert res_design.blend_with is None
    assert res_design.confidence >= 0.60


def test_se_shallow_depth():
    """
    Verifies that in the SE domain, Socratic deepening caps at 1 cycle on closure ("I don't know").
    Turn 1: SE statement with distortion -> S2_CLARIFY (active detection, deepen_count=0)
    Turn 2: "I don't know" -> Deepening Cycle 1 (deepen_count=1)
    Turn 3: Second "I don't know" -> Resolves detection immediately rather than triggering a 3rd probe.
    """
    orchestrator = ThinkingPartnerOrchestrator()
    graph = ProblemGraph()

    # Turn 1: Problem intake
    resp1, graph, art1 = orchestrator.process_turn(
        graph, "Our checkout latency is degrading under load and we can't scale the database replicas."
    )
    assert graph.current_domain == "se"
    assert graph.current_phase == StatePhase.S2_CLARIFY
    target_det_id = graph.active_detection_id
    assert target_det_id is not None
    det = next(d for d in graph.detections if d.id == target_det_id)
    assert det.deepen_count == 0

    # Turn 2: First closure ("I don't know") -> Deepen Cycle 1
    resp2, graph, art2 = orchestrator.process_turn(graph, "I don't know")
    assert det.deepen_count == 1
    assert not det.resolved

    # Turn 3: Second closure ("I don't know") -> Caps at 1 cycle, resolves detection
    resp3, graph, art3 = orchestrator.process_turn(graph, "I don't know")
    assert det.deepen_count == 1
    assert det.resolved is True


def test_leadership_deep_depth():
    """
    Verifies that in the Leadership domain, Socratic deepening allows 2 full cycles on closure.
    Turn 1: Leadership statement -> S2_CLARIFY (active detection, deepen_count=0)
    Turn 2: "that's the only thing" -> Deepening Cycle 1 (deepen_count=1)
    Turn 3: "I don't know" -> Deepening Cycle 2 (deepen_count=2)
    Turn 4: Concrete answer -> Resolves detection.
    """
    orchestrator = ThinkingPartnerOrchestrator()
    graph = ProblemGraph()

    # Turn 1: Problem intake
    resp1, graph, art1 = orchestrator.process_turn(
        graph, "They don't think I'm leadership material because I'm not loud in executive meetings."
    )
    assert graph.current_domain == "leadership"
    assert graph.current_phase == StatePhase.S2_CLARIFY
    target_det_id = graph.active_detection_id
    det = next(d for d in graph.detections if d.id == target_det_id)
    assert det.deepen_count == 0

    # Turn 2: First closure -> Deepening Cycle 1
    resp2, graph, art2 = orchestrator.process_turn(graph, "that's the only thing")
    assert det.deepen_count == 1
    assert not det.resolved

    # Turn 3: Second closure -> Deepening Cycle 2
    resp3, graph, art3 = orchestrator.process_turn(graph, "I don't know")
    assert det.deepen_count == 2
    assert not det.resolved

    # Turn 4: Concrete answer -> Resolves detection
    resp4, graph, art4 = orchestrator.process_turn(
        graph, "Alex told me directly after the review that the VP wants a louder presence."
    )
    assert det.resolved is True


def test_capture_cue_closes_se():
    """
    Verifies that in the SE domain, explicit capture/close cues advance immediately to outcome.
    Turn 1: Multi-distortion SE statement
    Turn 2: "Let's capture this as done" -> Immediately resolves all pending detections and jumps to S3_OUTCOME.
    """
    orchestrator = ThinkingPartnerOrchestrator()
    graph = ProblemGraph()

    # Turn 1: SE statement with multiple distortions
    resp1, graph, art1 = orchestrator.process_turn(
        graph, "Our checkout latency is degrading under load, every time we add replicas it gets worse, it's just the database."
    )
    assert graph.current_domain == "se"
    assert graph.current_phase == StatePhase.S2_CLARIFY
    assert len(graph.detections) >= 2

    # Turn 2: Early capture cue
    resp2, graph, art2 = orchestrator.process_turn(graph, "Let's capture this as done.")
    assert graph.current_phase == StatePhase.S3_OUTCOME
    assert all(d.resolved for d in graph.detections)
