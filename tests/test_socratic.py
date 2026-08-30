"""Unit tests for the Socratic messaging layer, closure detector, and deepening ladder."""

import pytest
from thinking_partner.agent.socratic import SocraticRouter, PATTERN_ROUTER_TABLE, FRAMING_STRINGS
from thinking_partner.agent.models import DetectionNode, PatternType, SocraticIntent, DeepeningTechnique


def test_closure_detector():
    # Closures
    assert SocraticRouter.is_closure("I don't know") is True
    assert SocraticRouter.is_closure("that's it") is True
    assert SocraticRouter.is_closure("that's the only thing") is True
    assert SocraticRouter.is_closure("it's obvious") is True
    assert SocraticRouter.is_closure("yes") is True

    # Non-closures (concrete evidence)
    assert SocraticRouter.is_closure("In Tuesday's standup, Alex interrupted me twice and skipped my slide.") is False
    assert SocraticRouter.is_closure("We have 3 weeks of runway and $12k in MRR.") is False


def test_socratic_base_routing():
    det = DetectionNode(
        utterance_id="utt_1",
        pattern=PatternType.MIND_READING,
        surface="they think I'm incompetent",
        span=[0, 26],
    )
    q_node = SocraticRouter.route_base_question(det)

    assert q_node.socratic_intent == SocraticIntent.PROBE_EVIDENCE
    assert q_node.deepen_cycle == 0
    assert "they think I'm incompetent" in q_node.text


def test_all_patterns_in_router_table():
    for pattern in PatternType:
        assert pattern in PATTERN_ROUTER_TABLE
        intent, template_id, base_tmpl = PATTERN_ROUTER_TABLE[pattern]
        assert isinstance(intent, SocraticIntent)
        assert len(template_id) > 0
        assert len(base_tmpl) > 0


def test_bedrock_framing_strings_exist():
    assert len(FRAMING_STRINGS) >= 4
    for k, s in FRAMING_STRINGS.items():
        assert isinstance(s, str)
        assert len(s) > 5


def test_deepening_ladder_progression():
    det = DetectionNode(
        utterance_id="utt_1",
        pattern=PatternType.MIND_READING,
        surface="they don't see me as a leader",
        span=[0, 29],
    )

    # Cycle 1 Deepening: Observation vs interpretation split
    q_cycle_1 = SocraticRouter.route_deepening_question(det, current_cycle=1, last_answer="that's the only thing")
    assert q_cycle_1.deepen_cycle == 1
    assert q_cycle_1.technique == DeepeningTechnique.OBSERVATION_SPLIT

    # Cycle 2 Deepening: Metacognitive nudge
    q_cycle_2 = SocraticRouter.route_deepening_question(det, current_cycle=2, last_answer="I don't know")
    assert q_cycle_2.deepen_cycle == 2
    assert q_cycle_2.technique == DeepeningTechnique.METACOGNITIVE_NUDGE


def test_clean_language_template_formatting():
    det = DetectionNode(
        utterance_id="utt_clean",
        pattern=PatternType.CAUSE_EFFECT,
        surface="his delay makes me fail",
        span=[0, 24],
    )
    q_node = SocraticRouter.route_base_question(det)
    # Verbatim reuse check (David Grove clean language invariant)
    assert "his delay makes me fail" in q_node.text
