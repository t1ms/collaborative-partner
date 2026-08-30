"""Unit tests for the MetaModelClassifier and Layer Tagger."""

import pytest
from thinking_partner.agent.classifier import MetaModelClassifier, PATTERN_PRIORITY
from thinking_partner.agent.models import PatternType, LayerType


def test_classifier_pattern_detection():
    classifier = MetaModelClassifier()

    # Mind Reading
    dets = classifier.classify("They don't think I'm leadership material", "utt_1")
    patterns = [d.pattern for d in dets]
    assert PatternType.MIND_READING in patterns

    # Universal Quantifier & Modal Necessity
    dets = classifier.classify("I always have to do everything myself or it fails", "utt_2")
    patterns = [d.pattern for d in dets]
    assert PatternType.UNIVERSAL_QUANTIFIER in patterns
    assert PatternType.MODAL_NECESSITY in patterns


def test_all_eleven_patterns_detected():
    classifier = MetaModelClassifier()
    test_cases = [
        ("He makes me angry every time", PatternType.CAUSE_EFFECT),
        ("They assume I won't succeed", PatternType.MIND_READING),
        ("Her silence means that she disagrees", PatternType.COMPLEX_EQUIVALENCE),
        ("It's bad to make mistakes here", PatternType.LOST_PERFORMATIVE),
        ("Everyone knows this won't work", PatternType.UNIVERSAL_QUANTIFIER),
        ("I must finish this tonight", PatternType.MODAL_NECESSITY),
        ("I can't push back on the timeline", PatternType.MODAL_POSSIBILITY),
        ("I'm stuck on this problem", PatternType.SIMPLE_DELETION),
        ("This solution is better than before", PatternType.COMPARATIVE_DELETION),
        ("They are undermining the whole project", PatternType.UNSPECIFIED_VERB),
        ("People are frustrating to deal with", PatternType.UNSPECIFIED_REFERENT),
    ]
    for text, expected_pattern in test_cases:
        dets = classifier.classify(text, "test_utt")
        patterns = [d.pattern for d in dets]
        assert expected_pattern in patterns, f"Failed to detect {expected_pattern} in '{text}'"


def test_dual_horizon_layer_tagging():
    classifier = MetaModelClassifier()

    # Upstream state
    layer_upstream = classifier.determine_layer("I am completely exhausted and burned out from work")
    assert layer_upstream == LayerType.UPSTREAM_STATE

    # Downstream symptom
    layer_downstream = classifier.determine_layer("I missed the standup and delayed the email pitch")
    assert layer_downstream == LayerType.DOWNSTREAM_SYMPTOM


def test_priority_selection():
    classifier = MetaModelClassifier()

    # Mixed statement with Distortion (mind_reading) and Deletion (comparative)
    dets = classifier.classify("They think I'm incompetent because I'm not faster than Sarah", "utt_3")
    highest = classifier.select_highest_priority(dets)
    assert highest is not None
    assert highest.pattern == PatternType.MIND_READING


def test_char_spans_and_confidence():
    classifier = MetaModelClassifier()
    dets = classifier.classify("I can't push back", "utt_4")
    assert len(dets) > 0
    d = dets[0]
    assert d.span[0] >= 0
    assert d.span[1] > d.span[0]
    assert d.confidence >= 0.70
