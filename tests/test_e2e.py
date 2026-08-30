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
