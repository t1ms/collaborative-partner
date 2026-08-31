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


def test_novice_scanning_se_classification():
    """
    Verifies that a novice tooling / scripting problem statement
    locks into the SE domain on Turn 1.
    """
    res = classify_domain(
        "i want to vibe code a scanning software because buying one is so expensive",
        prev_domain="general",
    )
    assert res.domain == "se"
    assert res.confidence >= 0.60


def test_se_tooling_pragmatic_alternative():
    """
    Verifies that in SE domain, build-vs-buy and tooling queries route to pragmatic alternative
    probing (e.g. testing free drivers/utilities before writing custom code).
    """
    orchestrator = ThinkingPartnerOrchestrator()
    graph = ProblemGraph()

    # Turn 1: Problem statement -> immediately catches build-vs-buy constraint
    resp1, graph, art1 = orchestrator.process_turn(
        graph, "i want to vibe code a scanning software because buying one is so expensive"
    )
    assert graph.current_domain == "se"
    assert graph.current_phase == StatePhase.S2_CLARIFY
    assert any(k in resp1.lower() for k in ["free", "driver", "naps2", "kodak", "utility", "build-versus-buy", "custom software", "capture"])

    # Turn 2: User provides closure on hardware / batch requirement
    resp2, graph, art2 = orchestrator.process_turn(
        graph, "i have a kodak scanner available and need to scan files"
    )
    assert graph.current_domain == "se"
    assert graph.current_phase in (StatePhase.S2_CLARIFY, StatePhase.S3_OUTCOME)


def test_classify_domain_llm_override():
    """
    Verifies that a single-keyword utterance is swayed by a high-confidence LLM semantic hint,
    while in the absence of LLM hint the single keyword is insufficient to trigger a cold-start false positive.
    """
    # 1. With LLM hint 'leadership' (conf=0.9) on single keyword ("api"), leadership wins (1.5 > 1.0)
    res_llm = classify_domain(
        "I am struggling with how to handle this API conversation.",
        prev_domain="general",
        llm_hint="leadership",
        llm_conf=0.9,
    )
    assert res_llm.domain == "leadership"
    assert res_llm.scores["leadership"] >= 1.5
    assert res_llm.confidence >= 0.60

    # 2. Without LLM hint, single keyword alone does not have sufficient signal (1.0 < 2.0)
    res_no_llm = classify_domain(
        "I am struggling with how to handle this API conversation.",
        prev_domain="general",
        llm_hint=None,
    )
    assert res_no_llm.domain == "general"


def test_classify_domain_llm_beaten_by_strong_keywords():
    """
    Verifies that multiple strong domain keywords (score >= 2.0) beat an opposing single LLM hint (weight 1.5),
    preserving deterministic anchor priority against hallucinated hints.
    """
    res = classify_domain(
        "Our checkout p95 latency is 900ms and PagerDuty alerts are firing on the replica.",
        prev_domain="general",
        llm_hint="leadership",
        llm_conf=0.9,
    )
    # SE keywords (checkout, p95, latency, pagerduty, replica) total > 2.0, beating leadership (1.5)
    assert res.domain == "se"
    assert res.scores["se"] > res.scores["leadership"]


def test_classify_domain_low_confidence_llm_ignored():
    """
    Verifies that low confidence LLM hints (< 0.50) are safely ignored and do not affect scoring.
    """
    res = classify_domain(
        "Can you help me think through this situation?",
        prev_domain="general",
        llm_hint="leadership",
        llm_conf=0.30,
    )
    assert res.scores["leadership"] == 0.0
    assert res.domain == "general"


def test_orchestrator_llm_domain_classification_flow(monkeypatch):
    """
    Verifies that when the orchestrator's LLM classifier returns a hint,
    it flows seamlessly through process_turn and guides domain selection.
    """
    orchestrator = ThinkingPartnerOrchestrator()
    graph = ProblemGraph()

    # Monkeypatch the LLM classifier helper on the orchestrator instance
    monkeypatch.setattr(
        orchestrator,
        "_classify_domain_llm",
        lambda text: ("leadership", 0.95),
    )
    # Enable use_real_llm flag to simulate active LLM connection
    orchestrator.use_real_llm = True

    resp, graph, art = orchestrator.process_turn(
        graph, "I am struggling with how to handle this API conversation."
    )
    assert graph.current_domain == "leadership"
    assert "Outcome" in art.title or "Strategic" in art.title or "WFO" in art.title


def test_orchestrator_llm_malformed_json_fallback(monkeypatch):
    """
    Verifies that malformed JSON from the LLM gracefully falls back to (None, 0.0)
    without raising exceptions or corrupting the turn.
    """
    orchestrator = ThinkingPartnerOrchestrator()
    orchestrator.use_real_llm = True

    # Mock client generate_content returning unparseable text
    class MockBadResponse:
        text = "This is not json {bad_json"

    class MockClient:
        class models:
            @staticmethod
            def generate_content(*args, **kwargs):
                return MockBadResponse()

    orchestrator.client = MockClient()

    dom, conf = orchestrator._classify_domain_llm("test text")
    assert dom is None
    assert conf == 0.0


def test_orchestrator_llm_invalid_enum_fallback(monkeypatch):
    """
    Verifies that unexpected domain values outside the allowed enum fall back to None.
    """
    orchestrator = ThinkingPartnerOrchestrator()
    orchestrator.use_real_llm = True

    class MockEnumResponse:
        text = '{"domain": "unsupported_domain_xyz", "confidence": 0.9, "reason": "test"}'

    class MockClient:
        class models:
            @staticmethod
            def generate_content(*args, **kwargs):
                return MockEnumResponse()

    orchestrator.client = MockClient()

    dom, conf = orchestrator._classify_domain_llm("test text")
    assert dom is None


def test_server_source_type_allowlist_validation():
    """
    Verifies that FastAPI / Pydantic ChatRequest enforces the source_type allowlist.
    """
    from thinking_partner.server import ChatRequest
    import pydantic

    # Allowed source types should pass and be normalized
    req_valid = ChatRequest(message="Hello", source_type="GitHub")
    assert req_valid.source_type == "github"

    req_valid_domain = ChatRequest(message="Hello", source_type="SE")
    assert req_valid_domain.source_type == "se"

    # Arbitrary / invalid source types must raise ValidationError
    with pytest.raises(pydantic.ValidationError):
        ChatRequest(message="Hello", source_type="arbitrary_injected_boost")


def test_session_turn_limit_auto_captures_adr(monkeypatch):
    """
    Verifies that reaching SESSION_MAX_TURNS automatically concludes in S6_DONE
    and returns a graceful ADR artifact and limit_hit=True.
    """
    from thinking_partner.server import app, store
    from fastapi.testclient import TestClient

    client = TestClient(app)
    # Create a fresh session
    res_new = client.post("/api/session/new")
    session_id = res_new.json()["session_id"]

    # Pre-populate graph with 40 utterances
    graph = store.load(session_id)
    from thinking_partner.agent.models import UtteranceNode
    for i in range(40):
        graph.utterances.append(UtteranceNode(text=f"Turn {i}", speaker="user"))
    store.save(graph)

    # Trigger next turn at capacity
    res_chat = client.post("/api/chat", json={"session_id": session_id, "message": "Another turn"})
    assert res_chat.status_code == 200
    data = res_chat.json()
    assert data["limit_hit"] is True
    assert data["current_phase"] == "S6_DONE"
    assert "session capacity" in data["response"]
    assert data["latest_artifact"] is not None


def test_rate_limit_enforcement_429():
    """
    Verifies that sending more than RATE_LIMIT_TURNS_PER_MIN in 60s returns HTTP 429.
    """
    import time
    from thinking_partner.server import app, store
    from fastapi.testclient import TestClient

    client = TestClient(app)
    res_new = client.post("/api/session/new")
    session_id = res_new.json()["session_id"]

    # Pre-populate 10 timestamps in the last 10 seconds
    graph = store.load(session_id)
    now = time.time()
    graph.turn_timestamps = [now - i for i in range(10)]
    store.save(graph)

    # Next request should trigger 429
    res_chat = client.post("/api/chat", json={"session_id": session_id, "message": "Spam turn"})
    assert res_chat.status_code == 429
    assert "Rate limit exceeded" in res_chat.json()["detail"]


def test_token_accounting_accumulation():
    """
    Verifies that turn execution records timestamps and accumulates total_output_tokens.
    """
    orchestrator = ThinkingPartnerOrchestrator()
    graph = ProblemGraph()

    resp, graph, art = orchestrator.process_turn(
        graph, "Our checkout p95 latency is 900ms under load."
    )
    assert len(graph.turn_timestamps) == 1
    assert graph.total_output_tokens >= 0


def test_payload_length_validation():
    """
    Verifies that overly long message payloads (>2000 chars) are rejected with ValidationError.
    """
    from thinking_partner.server import ChatRequest, IngestRequest
    import pydantic

    # 2000 char message should succeed
    req_valid = ChatRequest(message="a" * 2000)
    assert len(req_valid.message) == 2000

    # 2001 char message must fail
    with pytest.raises(pydantic.ValidationError):
        ChatRequest(message="a" * 2001)

    # 10000 char ingest should succeed
    req_ingest_valid = IngestRequest(source_name="test", raw_text="a" * 10000)
    assert len(req_ingest_valid.raw_text) == 10000

    # 10001 char ingest must fail
    with pytest.raises(pydantic.ValidationError):
        IngestRequest(source_name="test", raw_text="a" * 10001)


def test_chat_response_turns_remaining():
    """
    Verifies that chat responses return accurate turns_remaining counts.
    """
    from thinking_partner.server import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    res_new = client.post("/api/session/new")
    session_id = res_new.json()["session_id"]

    res_chat = client.post("/api/chat", json={"session_id": session_id, "message": "First problem turn"})
    assert res_chat.status_code == 200
    data = res_chat.json()
    assert "turns_remaining" in data
    assert data["turns_remaining"] == 39  # 40 - 1


def test_store_lru_cache_eviction(tmp_path):
    """
    Verifies that ProblemGraphStore evicts oldest in-memory session when exceeding max_sessions.
    """
    from thinking_partner.graph.store import ProblemGraphStore
    from thinking_partner.agent.models import ProblemGraph

    store = ProblemGraphStore(storage_dir=tmp_path, max_sessions=3)
    g1 = ProblemGraph(session_id="ses_1")
    g2 = ProblemGraph(session_id="ses_2")
    g3 = ProblemGraph(session_id="ses_3")
    g4 = ProblemGraph(session_id="ses_4")

    store.save(g1)
    store.save(g2)
    store.save(g3)
    assert len(store._memory_cache) == 3
    assert "ses_1" in store._memory_cache

    # Adding 4th should evict ses_1 from memory cache (persisted to disk)
    store.save(g4)
    assert len(store._memory_cache) == 3
    assert "ses_1" not in store._memory_cache
    assert "ses_4" in store._memory_cache

    # Loading ses_1 from disk brings it back and evicts ses_2
    loaded = store.load("ses_1")
    assert loaded is not None
    assert "ses_1" in store._memory_cache
    assert "ses_2" not in store._memory_cache







