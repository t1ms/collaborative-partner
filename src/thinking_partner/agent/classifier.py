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
        r"(they (don't think|think|believe|feel|assume|see me as)|she knows|he thinks|everybody thinks|people think|they assume|boss thinks|investors feel|they don't see me as)",
        0.95,
    ),
    (
        PatternType.CAUSE_EFFECT,
        r"(\b(makes me|causes( me)? to|forces me to|drives me to|results in( me)?|leads to|caused by|due to|because of|(it's )?just the \w+|so i (shouldn't|must|can't))\b)",
        0.92,
    ),
    (
        PatternType.COMPLEX_EQUIVALENCE,
        r"(\bmeans that\b|\bequals\b|\bmeans they\b|\bif .* then it means\b|\bshows that i'm\b|\bmeans i\b|\bmeans we\b)",
        0.90,
    ),
    (
        PatternType.META_FRAME,
        r"(\bi hate that i\b|\bi feel guilty (that|about)\b|\bfrustrated with myself for\b|\bjudging myself for\b)",
        0.92,
    ),
    (
        PatternType.UNIVERSAL_QUANTIFIER,
        r"\b(always|never|every time|everyone|everybody|nobody|every single|all of them|none of them)\b",
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
        r"\b(it's (bad|wrong|unprofessional|unacceptable|essential|critical) to\b|\bone shouldn't\b|\bshouldn't\b)",
        0.85,
    ),
    (
        PatternType.COMPARATIVE_DELETION,
        r"\b(expensive|cheap|costly|faster|better|worse|easier|harder|more productive|less effective|too slow|too much|too high|too low|higher|lower|slower|degrading)\b",
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
        r"\b(i'm stuck|i'm overwhelmed|this is broken|it's impossible|it failed|can't decide|latency issue|latency problem|degrading under load|performance issue|broken)\b",
        0.78,
    ),
]


import logging
import re
from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field
from .models import PatternType, LayerType, DetectionNode
from .overlays import load_domain_packs, get_domain_pack, DomainPack
from ..config import (
    DOMAIN_SWITCH_THRESHOLD,
    DOMAIN_MARGIN,
    DOMAIN_HYSTERESIS,
    DOMAIN_BLEND,
    DOMAIN_LLM_WEIGHT,
)

logger = logging.getLogger("thinking_partner.classifier")

# Safe non-crisis idiom patterns to exclude from self-harm classification
NON_CRISIS_IDIOMS = [
    r"\b(deadline|deadlines|workload|backlog|meeting|meetings|traffic|bug|queue|latency|server|boss|job)\s+(is|are)\s+killing me\b",
    r"\b(killing it|killing me with|dying of laughter|dying to see|dying to know|dying for)\b",
]

IMMINENT_CRISIS_PHRASES = [
    r"\b(want to die|kill myself|end it all|end my life|commit suicide|take my own life|gonna kill myself|going to kill myself|ending it all)\b.*\b(tonight|today|now|right now|immediately)\b",
    r"\b(tonight|today|now|right now|immediately)\b.*\b(want to die|kill myself|end it all|end my life|commit suicide|take my own life|gonna kill myself|going to kill myself|ending it all)\b",
    r"\b(want to die tonight|ending it all now|no reason to live tonight|gonna end it tonight|going to end it tonight)\b",
    r"\b(suicide tonight|suicide now|kill myself tonight|kill myself now)\b",
]

DISTRESS_CRISIS_PHRASES = [
    r"\b(want to die|wish i was dead|wish i were dead|no reason to live|can't go on anymore|cannot go on anymore|better off dead|nobody would miss me|nobody cares if i'm gone|hopeless and empty|feel like dying)\b",
    r"\b(empty inside and hopeless|severe depression and can't go on|nothing to live for)\b",
]

URGENT_HARM_CUES = [
    # Physical water/leak damage to equipment
    r"\b(leak|leaking|dripping|flood|flooding|water)\b.*\b(pc|computer|laptop|server|rack|outlet|desk|wet)\b",
    r"\b(will get wet|getting wet|soaked)\b",
    # Electrical/fire hazard & swollen battery hazard
    r"\b(sparking|sparks flying|outlet smoking|fire on the desk|short circuit|cable burning)\b",
    r"\b(swollen|swelling|bloated|bloating|punctured|puncturing|pierced|bulging|smoking)\b.*\b(battery|phone|device|laptop|macbook|ipad|cell|pack)\b",
    r"\b(battery|phone|device|laptop|macbook|ipad|cell|pack)\b.*\b(swollen|swelling|bloated|bloating|punctured|puncturing|pierced|bulging|smoking)\b",
    # Irreversible pending data destruction
    r"\b(rm -rf|drop database|drop table|delete from|truncate table)\b.*\b(prod|production|pending|accident|accidental|by mistake|run it now)\b",
    r"\b(about to rm -rf|pending rm -rf|executing rm -rf)\b",
]

PRAGMATIC_ACTION_CUES = [
    # Physical repairs, swaps, hardware maintenance & purchases (Archetype A)
    r"\b(open up|take apart|disassemble)\b.*\b(phone|iphone|android|device|laptop|macbook|pc|case|console)\b",
    r"\b(change|swap|replace|install|upgrade|repair)\b.*\b(battery|screen|display|ram|memory|ssd|hard drive|disk|fan|thermal paste|monitor)\b",
    r"\b(buy|buying|purchase|purchasing|get a new|shop for)\b.*\b(monitor|display|laptop|phone|keyboard|desk|chair|mouse|hardware)\b",
    # Scripting, scrapers, automated parsers, custom tools (Archetype B)
    r"\b(write|build|create)\b.*\b(script|scraper|parser|automation|bot|tool)\b.*\b(to |for |that |scrape|parse|extract|pull|fetch)\b",
    r"\b(scrape|scraping|parse|parsing)\b.*\b(pdf|pdfs|documents|pages|sites|urls|files|html)\b",
    # Large migrations, rewrites, build-vs-buy (Archetype B/D)
    r"\b(rewrite|rewriting)\b.*\b(in go|in rust|in python|in ts|in typescript|the backend|the frontend|the service|the engine)\b",
    r"\b(migrate|migrating)\b.*\b(postgres|database|db|mysql|redis|kafka|cluster|mongo|version)\b",
    r"\b(build|building)\b.*\b(our own|custom|in-house)\b.*\b(auth|authentication|oauth|billing|queue|payment)\b",
]


def is_crisis_imminent(text: str) -> bool:
    """
    Detects explicit, immediate threat of self-harm or suicide (Tier 1).
    Decoupled from domain keyword scoring; operates over multi-turn window.
    """
    text_lower = text.lower()
    for idiom in NON_CRISIS_IDIOMS:
        if re.search(idiom, text_lower):
            # Check if there is an explicit suicide phrase beyond the idiom
            if not any(re.search(pat, text_lower) for pat in [r"\b(kill myself|commit suicide|end my life)\b"]):
                return False

    for pattern in IMMINENT_CRISIS_PHRASES:
        if re.search(pattern, text_lower):
            return True
    return False


def is_crisis_distress(text: str) -> bool:
    """
    Detects chronic or severe emotional distress/hopelessness without explicit immediate suicide (Tier 3).
    """
    text_lower = text.lower()
    for idiom in NON_CRISIS_IDIOMS:
        if re.search(idiom, text_lower):
            if not any(re.search(pat, text_lower) for pat in [r"\b(want to die|no reason to live|better off dead)\b"]):
                return False

    for pattern in DISTRESS_CRISIS_PHRASES:
        if re.search(pattern, text_lower):
            return True
    return False


def is_urgent_harm(text: str) -> bool:
    """
    Detects acute physical hazard (leak, fire, swollen battery) or catastrophic pending data loss (Tier 2).
    """
    text_lower = text.lower()
    for pattern in URGENT_HARM_CUES:
        if re.search(pattern, text_lower):
            return True
    return False


def is_pragmatic_action(text: str) -> bool:
    """
    Detects concrete physical maintenance, setup/purchasing, scripting/scraping,
    or build-vs-buy implementation intents (Tier 4).
    """
    text_lower = text.lower()
    for pattern in PRAGMATIC_ACTION_CUES:
        if re.search(pattern, text_lower):
            return True
    return False


class DomainClassificationResult(BaseModel):
    domain: str = "general"
    blend_with: Optional[str] = None
    confidence: float = 0.50
    scores: Dict[str, float] = Field(default_factory=dict)
    candidate: str = "general"


def classify_domain(
    text: str,
    prev_domain: str = "general",
    domain_history: Optional[List[str]] = None,
    source_type: Optional[str] = None,
    llm_hint: Optional[str] = None,
    llm_conf: Optional[float] = None,
) -> DomainClassificationResult:
    """
    Scores domain keywords, applies ingest source boost, LLM semantic prior,
    and hysteresis, and returns (domain, blend_with, confidence, scores).
    """
    history = list(domain_history or [])
    packs = load_domain_packs()
    text_lower = text.lower()

    raw_scores: Dict[str, float] = {"se": 0.0, "design": 0.0, "leadership": 0.0}

    # Count keyword matches with word boundaries
    for dom_key in ["se", "design", "leadership"]:
        pack = packs.get(dom_key)
        if not pack:
            continue
        hit_count = 0
        for kw in pack.keywords:
            # Escape regex special characters in keywords
            kw_regex = r"\b" + re.escape(kw) + r"\b"
            if re.search(kw_regex, text_lower):
                hit_count += 1
        raw_scores[dom_key] = float(hit_count)

    # Ingest source boost
    if source_type:
        st = source_type.lower()
        if any(k in st for k in ["repo", "github", "code", "log", "metrics", "telemetry", "trace", "se"]):
            raw_scores["se"] += 2.0
        elif any(k in st for k in ["figma", "design", "wireframe", "prototype", "user", "ux"]):
            raw_scores["design"] += 2.0
        elif any(k in st for k in ["1-on-1", "slack", "meeting", "roadmap", "stakeholder", "exec", "leadership"]):
            raw_scores["leadership"] += 2.0

    # LLM semantic prior boost (treats None as legacy pass, drops explicit < 0.50)
    if llm_hint and llm_hint in raw_scores and (llm_conf is None or llm_conf >= 0.50):
        raw_scores[llm_hint] += DOMAIN_LLM_WEIGHT

    # Apply tiny previous domain bias
    if prev_domain in raw_scores and raw_scores[prev_domain] > 0:
        raw_scores[prev_domain] += 0.05

    # Sort scores descending
    sorted_scores = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
    top_dom, top_score = sorted_scores[0]
    second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0.0

    # Calculate confidence
    if top_score == 0.0:
        candidate = "general"
        confidence = 0.50
    else:
        candidate = top_dom
        confidence = min(0.99, 0.40 + 0.15 * top_score)

    # Determine winning domain with margin check (requires 2+ keyword hits, source boost, or LLM prior to avoid single-word false positives)
    has_sufficient_signal = (
        (top_score >= 2.0)
        or (top_score >= 1.0 and bool(source_type))
        or (top_score >= DOMAIN_LLM_WEIGHT and bool(llm_hint))
    )
    if confidence >= DOMAIN_SWITCH_THRESHOLD and (top_score - second_score >= DOMAIN_MARGIN) and has_sufficient_signal:
        winning_candidate = candidate
    else:
        winning_candidate = prev_domain

    # Hysteresis & Blending State Resolution
    result_domain = prev_domain
    blend_with: Optional[str] = None

    if prev_domain == "general" or not prev_domain:
        # Cold start: immediate lock if confident candidate found
        result_domain = winning_candidate
        blend_with = None
    elif winning_candidate == prev_domain:
        # Stable in current domain
        result_domain = prev_domain
        blend_with = None
    elif winning_candidate == "general":
        # Neutral input: retain active domain
        result_domain = prev_domain
        blend_with = None
    else:
        # In-flight domain jump attempt
        # Check if the previous candidate in history was also this candidate (2-turn confirmation)
        if history and history[-1] == winning_candidate:
            # Confirmed 2nd consecutive hit -> hard switch
            result_domain = winning_candidate
            blend_with = None
        else:
            # Single-turn jump -> stay in prev_domain with 1-turn blend
            result_domain = prev_domain
            blend_with = winning_candidate if DOMAIN_BLEND else None

    logger.info(
        f"[Classifier] domain={result_domain} candidate={winning_candidate} "
        f"llm_hint={llm_hint} llm_conf={llm_conf} top_score={top_score:.2f} "
        f"blend_with={blend_with}"
    )

    return DomainClassificationResult(
        domain=result_domain,
        blend_with=blend_with,
        confidence=confidence,
        scores=raw_scores,
        candidate=winning_candidate,
    )


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

    def classify(
        self,
        utterance_text: str,
        utterance_id: str,
        prev_domain: str = "general",
        llm_hint: Optional[str] = None,
        llm_conf: Optional[float] = None,
    ) -> List[DetectionNode]:
        """Deterministic regex-based classification with dual-horizon layer tagging and domain hint."""
        detections: List[DetectionNode] = []
        text_lower = utterance_text.lower()
        overall_layer = self.determine_layer(utterance_text)

        domain_res = classify_domain(
            utterance_text,
            prev_domain=prev_domain,
            llm_hint=llm_hint,
            llm_conf=llm_conf,
        )

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
                    domain_hint=domain_res.domain,
                    domain_confidence=domain_res.confidence,
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
