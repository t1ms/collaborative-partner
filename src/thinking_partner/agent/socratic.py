"""Socratic Messaging Layer: Router, Template Generation, Bedrock Framing, and Deepening Ladder.

Scientific Lineage & Attribution:
- Socratic Questioning Taxonomy (8 Moves): Paul & Elder (2006), *Critical Thinking*
- Meta-Model Interrogative Forms: Bandler & Grinder (1975), *The Structure of Magic I*
- Working Alliance & Brevity Optimization: CARE (2026, arXiv:2602.20648) & EMMI (2024, arXiv:2406.16478)
- Ladder of Abstraction Navigation: S. I. Hayakawa (1949), *Language in Thought and Action*
"""

import re
from typing import Optional, Tuple, Dict
from .models import (
    PatternType,
    SocraticIntent,
    DeepeningTechnique,
    DetectionNode,
    QuestionNode,
    AnswerNode,
)

# Canonical Pattern -> (SocraticIntent, TemplateId, BaseTemplate)
PATTERN_ROUTER_TABLE: Dict[PatternType, Tuple[SocraticIntent, str, str]] = {
    PatternType.SIMPLE_DELETION: (
        SocraticIntent.CLARIFICATION,
        "simple_deletion_1",
        "When you say '[surface]', what specifically are you pointing at?",
    ),
    PatternType.COMPARATIVE_DELETION: (
        SocraticIntent.PROBE_CRITERIA,
        "comparative_deletion_1",
        "Faster than what — what's the benchmark you're measuring against?",
    ),
    PatternType.UNSPECIFIED_REFERENT: (
        SocraticIntent.PROBE_ASSUMPTION,
        "unspecified_referent_1",
        "You said '[surface]' — what made that feel like one actor / one mind?",
    ),
    PatternType.UNSPECIFIED_VERB: (
        SocraticIntent.CLARIFICATION,
        "unspecified_verb_1",
        "When you say '[surface]', what exactly did they do or say?",
    ),
    PatternType.CAUSE_EFFECT: (
        SocraticIntent.PROBE_CAUSAL_LINK,
        "cause_effect_1",
        "How does '[surface]' actually produce that result — and what if it didn't?",
    ),
    PatternType.MIND_READING: (
        SocraticIntent.PROBE_EVIDENCE,
        "mind_reading_1",
        "When you say '[surface]', what did you actually see or hear that tells you that?",
    ),
    PatternType.COMPLEX_EQUIVALENCE: (
        SocraticIntent.PROBE_EQUATION,
        "complex_equivalence_1",
        "How does '[surface]' come to equal that — what link are you drawing?",
    ),
    PatternType.LOST_PERFORMATIVE: (
        SocraticIntent.PROBE_SOURCE,
        "lost_performative_1",
        "Who says that — where did that rule come from?",
    ),
    PatternType.UNIVERSAL_QUANTIFIER: (
        SocraticIntent.PROBE_ALTERNATIVE,
        "universal_quantifier_1",
        "Every time? Was there one moment it didn't — what was different?",
    ),
    PatternType.MODAL_NECESSITY: (
        SocraticIntent.PROBE_ASSUMPTION,
        "modal_necessity_1",
        "What would actually break if you didn't — what if another way were possible?",
    ),
    PatternType.MODAL_POSSIBILITY: (
        SocraticIntent.PROBE_BARRIER,
        "modal_possibility_1",
        "What exactly stands in the way — and what would have to be true for it to be possible?",
    ),
    PatternType.META_FRAME: (
        SocraticIntent.META_COGNITION,
        "meta_frame_1",
        "When you evaluate '[surface]', what happens if you treat it with curiosity rather than criticism?",
    ),
}

# Bedrock / Descend framing vocabulary
FRAMING_STRINGS = {
    SocraticIntent.PROBE_ASSUMPTION: "What's this actually resting on?",
    SocraticIntent.PROBE_CAUSAL_LINK: "Let's find what really drives this.",
    SocraticIntent.CLARIFICATION: "Back to what's actually being said.",
    SocraticIntent.PROBE_EVIDENCE: "What is this built on?",
    SocraticIntent.PROBE_ALTERNATIVE: "Stripped to zero, what has to be true?",
    SocraticIntent.PROBE_CRITERIA: "Let's calibrate the standard.",
    SocraticIntent.PROBE_EQUATION: "Let's separate the event from the meaning.",
    SocraticIntent.PROBE_SOURCE: "Where does this rule originate?",
    SocraticIntent.PROBE_BARRIER: "Let's map the boundary.",
    SocraticIntent.META_COGNITION: "Let's step outside the reaction for a moment.",
    "open": "Problems stack — each one rests on an assumption beneath it. Let's descend together to the load-bearing one.",
    "close": "Here's the bedrock this was sitting on — and the outcome that follows from it.",
}

# Closure cue words
CLOSURE_CUES = [
    r"\b(i don't know|idk|not sure|that's it|thats it|that's all|thats all|that's the only thing|thats the only thing|only one thing|just obvious|it's obvious|its obvious|nothing else|obviously)\b",
    r"^(yes|no|yeah|nah|yep|nope)$",
    r"\b(i just feel that way|it's self-evident|everyone knows)\b",
]


class SocraticRouter:
    """Deterministic Socratic Router and Deepening Protocol Engine."""

    @staticmethod
    def is_closure(answer_text: str) -> bool:
        """Detects if an answer is a shallow closure signal under-digging reasoning."""
        clean = answer_text.strip().lower()
        for cue in CLOSURE_CUES:
            if re.search(cue, clean):
                return True
        if len(clean.split()) <= 3 and not re.search(r"\b(because|when|told|said|showed|measured)\b", clean):
            return True
        return False

    @staticmethod
    def route_base_question(detection: DetectionNode) -> QuestionNode:
        """Emits the base (Cycle 0) Socratic Question for a detection."""
        intent, template_id, template_str = PATTERN_ROUTER_TABLE.get(
            detection.pattern,
            (
                SocraticIntent.CLARIFICATION,
                "generic_clarify_1",
                "When you say '[surface]', what specifically do you mean?",
            ),
        )

        framing = FRAMING_STRINGS.get(intent, "Back to what's actually being said.")
        question_text = template_str.replace("[surface]", detection.surface)

        return QuestionNode(
            targets_detection_id=detection.id,
            template_id=template_id,
            socratic_intent=intent,
            framing_string=framing,
            text=question_text,
            style="socratic",
            deepen_cycle=0,
            technique=None,
        )

    @staticmethod
    def route_deepening_question(
        detection: DetectionNode, current_cycle: int, last_answer: str
    ) -> QuestionNode:
        """Escalates through the per-pattern deepening ladder (Cycle 1 or 2)."""
        intent, template_id, _ = PATTERN_ROUTER_TABLE.get(
            detection.pattern,
            (SocraticIntent.CLARIFICATION, "generic_clarify_1", ""),
        )

        framing = "Let's pause on that for a second — let's stay right here."
        technique = DeepeningTechnique.EVIDENCE_LADDER
        text = ""

        if detection.pattern == PatternType.MIND_READING:
            if current_cycle == 1:
                technique = DeepeningTechnique.OBSERVATION_SPLIT
                framing = "Let's separate what was observed from what was concluded."
                text = "Literally — what were the exact words or actions? And what did you add on top of them?"
            else:
                technique = DeepeningTechnique.METACOGNITIVE_NUDGE
                framing = "We landed on that fast."
                text = "We landed on that very quickly — full stop, or is there a part of this you haven't said yet?"

        elif detection.pattern == PatternType.CAUSE_EFFECT:
            if current_cycle == 1:
                technique = DeepeningTechnique.EVIDENCE_LADDER
                framing = "Let's inspect the causal mechanism."
                text = f"If you point to the exact moment that links '{detection.surface}' to that reaction — what happened right before it?"
            else:
                technique = DeepeningTechnique.TEMPORAL_PROBE
                framing = "Tracing the timeline."
                text = "Did that reaction hit in the very second it happened, or did it build up afterward as you replayed it?"

        elif detection.pattern in (PatternType.MODAL_NECESSITY, PatternType.MODAL_POSSIBILITY):
            if current_cycle == 1:
                technique = DeepeningTechnique.POSITIVE_INTENT
                framing = "Looking at the protective intent."
                text = f"When you feel compelled to '{detection.surface}', what higher protective outcome is that keeping safe?"
            else:
                technique = DeepeningTechnique.OBSERVATION_SPLIT
                framing = "What is the concrete failure mode?"
                text = "What is the specific, observable catastrophe that happens if you don't do that?"

        elif detection.pattern == PatternType.UNIVERSAL_QUANTIFIER:
            if current_cycle == 1:
                technique = DeepeningTechnique.EVIDENCE_LADDER
                framing = "Searching for the counter-example."
                text = "Was there even one time where that wasn't true? What was different about that moment?"
            else:
                technique = DeepeningTechnique.METACOGNITIVE_NUDGE
                framing = "Testing the universal rule."
                text = "When we treat that as an absolute rule, what options does it immediately hide from view?"

        else:  # Deletions / unspecified referent / general fallback
            if current_cycle == 1:
                technique = DeepeningTechnique.EVIDENCE_LADDER
                framing = "Descend to a concrete moment."
                text = "If you had to pick one single concrete instance that illustrates this — what happened?"
            else:
                technique = DeepeningTechnique.METACOGNITIVE_NUDGE
                framing = "Metacognitive pause."
                text = "We landed on 'that's it' very quickly — is that the complete picture, or the easiest answer?"

        return QuestionNode(
            targets_detection_id=detection.id,
            template_id=f"{template_id}_deepen_{current_cycle}",
            socratic_intent=intent,
            framing_string=framing,
            text=text,
            style="socratic",
            deepen_cycle=current_cycle,
            technique=technique,
        )
