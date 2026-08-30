"""Unit tests for Problem Graph persistence, Taste Bank adaptation, and ADR mutation."""

import pytest
from pathlib import Path
from thinking_partner.agent.models import ProblemGraph, DetectionNode, PatternType, StatePhase, UtteranceNode, GraphEdge
from thinking_partner.graph.store import ProblemGraphStore
from thinking_partner.graph.taste_bank import TasteBank
from thinking_partner.tools.mutate_artifact import ArtifactMutationTool


def test_problem_graph_store_save_load(tmp_path):
    store = ProblemGraphStore(storage_dir=tmp_path)
    graph = ProblemGraph()
    graph.current_phase = StatePhase.S2_CLARIFY
    det = DetectionNode(
        utterance_id="utt_1",
        pattern=PatternType.CAUSE_EFFECT,
        surface="makes me shut down",
    )
    graph.detections.append(det)

    store.save(graph)

    loaded = store.load(graph.session_id)
    assert loaded is not None
    assert loaded.session_id == graph.session_id
    assert len(loaded.detections) == 1
    assert loaded.detections[0].surface == "makes me shut down"


def test_artifact_mutation_diff():
    tool = ArtifactMutationTool()
    graph = ProblemGraph()

    # Mutation 1: Initial empty
    art1 = tool.mutate(graph)
    assert art1.version == 1
    assert "Problem Architecture Record" in art1.content

    # Mutation 2: Add detection and mutate again
    graph.detections.append(
        DetectionNode(
            utterance_id="utt_1",
            pattern=PatternType.MIND_READING,
            surface="they think I'm weak",
            resolved=True,
        )
    )
    art2 = tool.mutate(graph)
    assert art2.version == 2
    assert len(art2.diff) > 0
    assert "+ | `mind_reading`" in art2.diff or "RESOLVED" in art2.diff


def test_graph_edges_and_node_integrity():
    graph = ProblemGraph()
    utt = UtteranceNode(text="I can't push back on timelines")
    det = DetectionNode(utterance_id=utt.id, pattern=PatternType.MODAL_POSSIBILITY, surface="can't")
    graph.utterances.append(utt)
    graph.detections.append(det)
    edge = GraphEdge(source_id=utt.id, target_id=det.id, edge_type="utterance->detection")
    graph.edges.append(edge)

    assert len(graph.edges) == 1
    assert graph.edges[0].source_id == utt.id
    assert graph.edges[0].edge_type == "utterance->detection"


def test_taste_bank_cross_session_adaptation(tmp_path):
    taste_bank = TasteBank(storage_dir=tmp_path)
    profile = taste_bank.get_profile("test_user_42")

    assert profile.user_id == "test_user_42"
    assert profile.depth_preference == "first_principles"  # default
    assert profile.sessions_completed == 0

    # Record successful session completion with deep descent
    updated = taste_bank.record_session_completion(
        user_id="test_user_42",
        resolved_count=2,
        deepen_count=3,
    )

    assert updated.sessions_completed == 1
    assert updated.depth_preference == "first_principles"
    assert updated.framing_anchor == "bedrock"
