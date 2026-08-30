"""End-to-end integration tests reproducing worked examples and full 5-phase flows."""

import pytest
from thinking_partner.agent.orchestrator import ThinkingPartnerOrchestrator
from thinking_partner.agent.models import ProblemGraph, StatePhase, PatternType, OutcomePredicateKey
from thinking_partner.tools.ingest_source import SourceIngestionTool
from fastapi.testclient import TestClient
from thinking_partner.server import app


def test_e2e_leadership_worked_example_variant_b():
    """
    Reproduces Variant B from worked-example-leadership.md:
    1. Utterance: 'They don't think I'm leadership material because I'm not loud in executive meetings.'
    2. Deepening 1: 'that's the only thing' -> triggers Cycle 1 Observation Split
    3. Deepening 2: 'I don't know' -> triggers Cycle 2 Metacognitive Nudge
    4. Concrete resolution: 'Alex said they needed someone who commands the room.' -> resolves detection
    5. Phase progression through S3 -> S4 -> S5 -> S6
    """
    orchestrator = ThinkingPartnerOrchestrator()
    graph = ProblemGraph()

    # Turn 1: Initial Problem Statement
    resp1, graph, art1 = orchestrator.process_turn(
        graph, "They don't think I'm leadership material because I'm not loud in executive meetings."
    )
    assert graph.current_phase == StatePhase.S2_CLARIFY
    assert len(graph.detections) >= 1
    assert any(k in resp1.lower() for k in ["see or hear", "tell you", "specific words", "think this"])

    # Turn 2: Shallow Closure 1 ("that's the only thing") -> Cycle 1
    resp2, graph, art2 = orchestrator.process_turn(graph, "that's the only thing")
    assert graph.current_phase == StatePhase.S2_CLARIFY
    assert any(k in resp2.lower() for k in ["exact words", "said or done", "literally", "landed on"])

    # Turn 3: Shallow Closure 2 ("I don't know") -> Cycle 2
    resp3, graph, art3 = orchestrator.process_turn(graph, "I don't know")
    assert graph.current_phase == StatePhase.S2_CLARIFY
    assert any(k in resp3.lower() for k in ["haven't said", "landed on", "part of this", "underneath"])

    # Turn 4: Concrete Observation -> Resolves Mind-Reading
    resp4, graph, art4 = orchestrator.process_turn(
        graph, "Alex told me directly after the review that the VP was looking for someone who commands the room."
    )
    mind_reading_det = next(d for d in graph.detections if d.pattern == PatternType.MIND_READING)
    assert mind_reading_det.resolved is True

    # Turn 5: WFO Positive Predicate
    resp5, graph, art5 = orchestrator.process_turn(
        graph, "I want to lead the infrastructure migration project with clear authority."
    )
    assert OutcomePredicateKey.POSITIVE in graph.outcome_predicates

    # Turn 6: WFO Self-Initiated Predicate
    resp6, graph, art6 = orchestrator.process_turn(
        graph, "Yes, by defining the technical roadmap and scheduling the architecture kickoff myself."
    )

    # Turn 7: WFO Sensory Evidence
    resp7, graph, art7 = orchestrator.process_turn(
        graph, "The team approves the RFC with zero unaddressed blocks and the VP signs off on the sprint backlog."
    )
    assert graph.current_phase in (StatePhase.S4_ANGLE, StatePhase.S5_ECOLOGY, StatePhase.S6_DONE)


def test_e2e_leadership_worked_example_variant_a():
    """Variant A: User immediately provides concrete evidence on Turn 2."""
    orchestrator = ThinkingPartnerOrchestrator()
    graph = ProblemGraph()

    orchestrator.process_turn(
        graph, "They don't think I'm leadership material because I'm not loud in executive meetings."
    )
    assert graph.current_phase == StatePhase.S2_CLARIFY

    # Immediate concrete observation
    resp2, graph, art2 = orchestrator.process_turn(
        graph, "In yesterday's review meeting, the VP explicitly said 'we need a more outspoken technical lead for this project'."
    )
    mind_reading_det = next(d for d in graph.detections if d.pattern == PatternType.MIND_READING)
    assert mind_reading_det.resolved is True
    assert graph.current_phase == StatePhase.S3_OUTCOME


def test_e2e_source_ingestion_tool():
    tool = SourceIngestionTool()
    graph = ProblemGraph()
    raw_text = "Transcript from 1-on-1 meeting:\nI feel overwhelmed and I have to do everything myself."
    node = tool.ingest_text_source(graph, "1-on-1", raw_text)

    assert len(graph.utterances) >= 1
    assert graph.utterances[0].id == node.id
    assert "[1-on-1]" in graph.utterances[0].text


def test_e2e_server_api_endpoints():
    client = TestClient(app)

    # Health check
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    # New session
    resp_new = client.post("/api/session/new")
    assert resp_new.status_code == 200
    session_id = resp_new.json()["session_id"]
    assert len(session_id) > 0

    # Chat turn
    resp_chat = client.post(
        "/api/chat",
        json={"session_id": session_id, "message": "I can't finish this proposal on time."},
    )
    assert resp_chat.status_code == 200
    data = resp_chat.json()
    assert "response" in data
    assert data["current_phase"] == "S2_CLARIFY"
    assert "latest_artifact" in data


def test_e2e_sre_system_deconstruction_and_bedrock_wfo():
    """
    Reproduces the SRE System Deconstruction flow:
    1. Multi-distortion utterance: universal_quantifier, cause_effect, comparative_deletion, simple_deletion.
    2. Deepening cycles (closure -> cycle 1 -> cycle 2 -> concrete resolution).
    3. Sequential resolution of all cognitive layers.
    4. Full 5-phase traversal to S6_DONE.
    5. Verifies ADR output contains >= 3 resolved distortions, testable WFO, and 1 trade-off constraint.
    """
    orchestrator = ThinkingPartnerOrchestrator()
    graph = ProblemGraph()

    turns = [
        "Our checkout latency is degrading under load, every time we add replicas it gets worse, it's just the database",
        "I don't know",
        "When profiling during load test, connection pool saturated at 50 max connections while app CPU was at 15%.",
        "Under 1x baseline traffic it handled 200 RPS fine, the bottleneck only triggered when traffic reached 3x.",
        "We need p95 latency under 500ms instead of 2400ms.",
        "The checkout service p95 spikes above 2400ms.",
        "under 500ms p95 @3x",
        "Yes, by configuring pgBouncer connection pooling myself.",
        "420ms flat 15m, queue <50",
        "The dashboard shows connection acquisition wait time dropping from 2300ms to 4ms.",
        "The only trade-off is 1 hour of maintenance window.",
    ]

    last_art = None
    last_resp = None
    for turn in turns:
        last_resp, graph, last_art = orchestrator.process_turn(graph, turn)

    assert graph.current_phase == StatePhase.S6_DONE
    assert graph.current_domain == "se"

    # Verify at least 3-4 distortions were detected and marked resolved
    resolved_dets = [d for d in graph.detections if d.resolved]
    assert len(resolved_dets) >= 3
    resolved_patterns = [d.pattern for d in resolved_dets]
    assert PatternType.CAUSE_EFFECT in resolved_patterns
    assert PatternType.UNIVERSAL_QUANTIFIER in resolved_patterns

    # Verify WFO predicates
    assert graph.outcome_predicates[OutcomePredicateKey.POSITIVE].statement == "under 500ms p95 @3x"
    assert "pgBouncer" in graph.outcome_predicates[OutcomePredicateKey.SELF_INITIATED].statement
    assert "420ms flat 15m" in graph.outcome_predicates[OutcomePredicateKey.SENSORY].statement

    # Verify Constraints
    assert len(graph.constraints) == 1
    assert "1 hour of maintenance" in graph.constraints[0].text

    # Verify live ADR content
    assert last_art is not None
    assert f"**Layers Peeled:** {len(resolved_dets)}" in last_art.content
    assert "✅ RESOLVED" in last_art.content
    assert "under 500ms p95 @3x" in last_art.content
    assert "420ms flat 15m, queue <50" in last_art.content
