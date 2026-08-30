"""Deterministic Meta-Model Classifier and Layer Tagger.

Scientific Lineage & Attribution:
- Linguistic Pattern Taxonomy: Bandler & Grinder (1975), *The Structure of Magic I & II*
- Transformational Grammar Roots: Noam Chomsky (1957, 1965)
- Clean Language Extraction Invariant: David Grove (1989)
- De-branding & Defensibility Protocol: Grounded per 02_map/VERIFICATION.md
"""

import re
from typing import List, Optional, Tuple
from .models import PatternType, LayerType, DetectionNode

# Priority order for detections: Distortions first (they fabricate structure) -> Deletions -> Modals/Quantifiers
PATTERN_PRIORITY = {
    PatternType.CAUSE_EFFECT: 10,
    PatternType.MIND_READING: 10,
    PatternType.COMPLEX_EQUIVALENCE: 10,
    PatternType.META_FRAME: 9,
    PatternType.UNSPECIFIED_REFERENT: 8,
    PatternType.UNSPECIFIED_VERB: 8,
    PatternType.SIMPLE_DELETION: 7,
    PatternType.LOST_PERFORMATIVE: 6,
    PatternType.MODAL_NECESSITY: 5,
    PatternType.MODAL_POSSIBILITY: 5,
    PatternType.UNIVERSAL_QUANTIFIER: 4,
    PatternType.COMPARATIVE_DELETION: 3,
}

# Regex and phrase cues for deterministic matching
UPSTREAM_STATE_CUES = [
    r"\b(tired|exhausted|burnout|burned out|depleted|drained|survival mode|barely getting by|overwhelmed|depressed|chronic|no energy)\b",
    r"\b(tank is empty|running on empty|empty tank|boundary collapse)\b",
]

DOWNSTREAM_SYMPTOM_CUES = [
    r"\b(on (my )?phone|scrolling|procrastinat\w+|slack|standup|email|deck|pitch|missed|late|kids|children|yell\w*|snap\w*|avoid\w*)\b",
    r"\b(don't think i'm leadership|not leadership material|won't listen|refused)\b",
]

PATTERNS_REGEX = [
    (
        PatternType.MIND_READING,
        r"(they (don't think|think|believe|feel)|she knows|he thinks|everybody thinks|people think|they assume|boss thinks|investors feel|they don't see me as)",
        0.95,
    ),
    (
        PatternType.CAUSE_EFFECT,
        r"(\b(makes me|causes me to|forces me to|because of .* i (can't|must)|drives me to|results in me)\b)",
        0.92,
    ),
    (
        PatternType.COMPLEX_EQUIVALENCE,
        r"(\bmeans that\b|\bequals\b|\bmeans they\b|\bif .* then it means\b|\bshows that i'm\b)",
        0.90,
    ),
    (
        PatternType.META_FRAME,
        r"(\bi hate that i\b|\bi feel guilty (that|about)\b|\bfrustrated with myself for\b|\bjudging myself for\b)",
        0.92,
    ),
    (
        PatternType.UNIVERSAL_QUANTIFIER,
        r"\b(always|never|every time|everyone|nobody|every single|all of them|none of them)\b",
        0.88,
    ),
    (
        PatternType.MODAL_NECESSITY,
        r"\b(must|have to|has to|need to|needs to|should|ought to)\b",
        0.85,
    ),
    (
        PatternType.MODAL_POSSIBILITY,
        r"\b(can't|cannot|impossible to|unable to|can never|no way to)\b",
        0.87,
    ),
    (
        PatternType.LOST_PERFORMATIVE,
        r"\b(it's (bad|wrong|unprofessional|unacceptable|essential|critical) to\b|\bone shouldn't\b)",
        0.85,
    ),
    (
        PatternType.COMPARATIVE_DELETION,
        r"\b(faster|better|worse|easier|harder|more productive|less effective|too slow|too much)\b",
        0.80,
    ),
    (
        PatternType.UNSPECIFIED_REFERENT,
        r"\b(they won't|they are|people are|leadership is|management is|the team is|they just)\b",
        0.82,
    ),
    (
        PatternType.UNSPECIFIED_VERB,
        r"\b(undermining|blocking|dismissing|ignoring|pushing me out|shutting me down)\b",
        0.80,
    ),
    (
        PatternType.SIMPLE_DELETION,
        r"\b(i'm stuck|i'm overwhelmed|this is broken|it's impossible|it failed|can't decide)\b",
        0.78,
    ),
]


class MetaModelClassifier:
    """Classifies user utterances into Meta-Model detections with confidence and layer tagging."""

    def __init__(self, use_gemini: bool = False, api_key: str = ""):
        self.use_gemini = use_gemini
        self.api_key = api_key

    def determine_layer(self, text: str) -> LayerType:
        """Dual-Horizon Triage: Tag whether utterance is upstream state or downstream symptom."""
        text_lower = text.lower()
        for cue in UPSTREAM_STATE_CUES:
            if re.search(cue, text_lower):
                return LayerType.UPSTREAM_STATE
        return LayerType.DOWNSTREAM_SYMPTOM

    def classify(self, utterance_text: str, utterance_id: str) -> List[DetectionNode]:
        """Deterministic regex-based classification with dual-horizon layer tagging."""
        detections: List[DetectionNode] = []
        text_lower = utterance_text.lower()
        overall_layer = self.determine_layer(utterance_text)

        # Check all pattern rules
        for pattern_type, regex_pattern, default_conf in PATTERNS_REGEX:
            match = re.search(regex_pattern, text_lower)
            if match:
                span_start, span_end = match.span()
                surface = utterance_text[span_start:span_end]

                # Specific detection layer determination
                det_layer = overall_layer
                if pattern_type == PatternType.META_FRAME or re.search(r"\b(exhausted|tired|burnout|drained)\b", surface.lower()):
                    det_layer = LayerType.UPSTREAM_STATE

                detection = DetectionNode(
                    utterance_id=utterance_id,
                    pattern=pattern_type,
                    span=[span_start, span_end],
                    surface=surface,
                    confidence=default_conf,
                    layer=det_layer,
                )
                detections.append(detection)

        # Sort detections by priority (Distortions first)
        detections.sort(key=lambda d: PATTERN_PRIORITY.get(d.pattern, 0), reverse=True)
        return detections

    def select_highest_priority(self, detections: List[DetectionNode]) -> Optional[DetectionNode]:
        """Picks the highest-priority unresolved detection."""
        unresolved = [d for d in detections if not d.resolved]
        if not unresolved:
            return None
        unresolved.sort(key=lambda d: (PATTERN_PRIORITY.get(d.pattern, 0), d.confidence), reverse=True)
        return unresolved[0]
