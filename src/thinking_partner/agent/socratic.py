"""Socratic Messaging Layer: Router, Template Generation, Bedrock Framing, and Deepening Ladder.

Scientific Lineage & Attribution:
- Socratic Questioning Taxonomy (8 Moves): Paul & Elder (2006), *Critical Thinking*
- Meta-Model Interrogative Forms: Bandler & Grinder (1975), *The Structure of Magic I*
- Working Alliance & Brevity Optimization: CARE (2026, arXiv:2602.20648) & EMMI (2024, arXiv:2406.16478)
- Ladder of Abstraction Navigation: S. I. Hayakawa (1949), *Language in Thought and Action*
"""

import re
from typing import Any, Dict, List, Optional, Tuple, Union
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
        "When you point at '[surface]', which specific parts, people, or instances are creating the biggest friction?",
    ),
    PatternType.UNSPECIFIED_VERB: (
        SocraticIntent.CLARIFICATION,
        "unspecified_verb_1",
        "When you say '[surface]', what specific actions, triggers, or steps are happening?",
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

DOMAIN_FRAMINGS: Dict[str, Dict[Any, str]] = {
    "se": {
        SocraticIntent.PROBE_ASSUMPTION: "What service dependency or architecture assumption is this actually resting on?",
        SocraticIntent.PROBE_CAUSAL_LINK: "Let's trace what telemetry or code path really triggers this behavior.",
        SocraticIntent.CLARIFICATION: "Back to the exact telemetry, queue metric, or error output.",
        SocraticIntent.PROBE_EVIDENCE: "What do the telemetry traces, dashboards, and p95 panels show?",
        SocraticIntent.PROBE_ALTERNATIVE: "Stripped to zero, what must the service contract guarantee?",
        SocraticIntent.PROBE_CRITERIA: "Let's calibrate against the latency, SLO, or throughput benchmark.",
        SocraticIntent.PROBE_EQUATION: "Let's separate the metric spike from the root failure assumption.",
        SocraticIntent.PROBE_SOURCE: "Where is that system constraint or config defined?",
        SocraticIntent.PROBE_BARRIER: "Let's isolate the failure bottleneck in the pipeline.",
        SocraticIntent.META_COGNITION: "Let's inspect the system assumptions without jumping to conclusions.",
        "open": "System problems stack — let's trace down to the load-bearing service bottleneck.",
        "close": "Here is the architectural bedrock — and the SLO-grounded outcome that follows.",
    },
    "design": {
        SocraticIntent.PROBE_ASSUMPTION: "What user mental model or expectation is this assuming?",
        SocraticIntent.PROBE_CAUSAL_LINK: "Let's trace how this interaction triggers the drop-off or friction.",
        SocraticIntent.CLARIFICATION: "Back to the exact UI state, screen, or user interaction.",
        SocraticIntent.PROBE_EVIDENCE: "What did you observe in the user journey, click path, or session replay?",
        SocraticIntent.PROBE_ALTERNATIVE: "What if the first-time user took a completely different path?",
        SocraticIntent.PROBE_CRITERIA: "What is the usability benchmark or task success rate we're measuring against?",
        SocraticIntent.PROBE_EQUATION: "Let's separate the user's drop-off action from their underlying goal.",
        SocraticIntent.PROBE_SOURCE: "Where is that UX guideline or pattern coming from?",
        SocraticIntent.PROBE_BARRIER: "What specifically blocks the user from completing the task?",
        SocraticIntent.META_COGNITION: "Let's step outside our builder assumptions to see the raw user flow.",
        "open": "User experience friction stacks — let's find the core mental model mismatch.",
        "close": "Here is the journey bedrock — and the user outcome that follows.",
    },
    "leadership": {
        SocraticIntent.PROBE_ASSUMPTION: "What organizational assumption or incentive is this resting on?",
        SocraticIntent.PROBE_CAUSAL_LINK: "Let's inspect what's driving this stakeholder dynamic.",
        SocraticIntent.CLARIFICATION: "Back to what was explicitly communicated or committed in writing.",
        SocraticIntent.PROBE_EVIDENCE: "What did you actually observe in the team commitments, 1-on-1s, or decision logs?",
        SocraticIntent.PROBE_ALTERNATIVE: "Is there an alternative alignment path that de-risks delivery for both sides?",
        SocraticIntent.PROBE_CRITERIA: "What standard or milestone are we measuring this against?",
        SocraticIntent.PROBE_EQUATION: "Let's separate the stakeholder's reaction from their underlying objective.",
        SocraticIntent.PROBE_SOURCE: "Who established that organizational rule or precedent?",
        SocraticIntent.PROBE_BARRIER: "What stands in the way of direct decision ownership?",
        SocraticIntent.META_COGNITION: "Let's step back from the interpersonal friction to view structural incentives.",
        "open": "Organizational challenges stack — let's descend to the core alignment bedrock.",
        "close": "Here is the alignment bedrock — and the clear outcome we own.",
    },
    "general": FRAMING_STRINGS,
}


def select_framing(domain: str = "general", intent: SocraticIntent = SocraticIntent.CLARIFICATION, blend_with: Optional[str] = None) -> str:
    """Selects domain-tailored framing string with optional 1-turn cross-domain blend."""
    dom = domain.lower() if domain else "general"
    pack_framings = DOMAIN_FRAMINGS.get(dom, DOMAIN_FRAMINGS["general"])
    base_framing = pack_framings.get(intent, FRAMING_STRINGS.get(intent, "Back to what's actually being said."))

    if blend_with and blend_with.lower() != dom and blend_with.lower() != "general":
        b_dom = blend_with.lower()
        if dom == "se" and b_dom == "leadership":
            return f"From product and stakeholder perspective on the payment queue and service telemetry: {base_framing}"
        elif dom == "se" and b_dom == "design":
            return f"Connecting user journey friction to backend telemetry: {base_framing}"
        elif dom == "design" and b_dom == "se":
            return f"Connecting backend latency to the user journey: {base_framing}"
        elif dom == "leadership" and b_dom == "se":
            return f"Looking at team delivery through the lens of service reliability: {base_framing}"
        else:
            return f"Bridging the {dom} context with {b_dom} considerations: {base_framing}"

    return base_framing


def sanitize_domain_output(text: str, domain: str = "general") -> str:
    """Removes forbidden phrases for the active domain and strips LaTeX."""
    dom = domain.lower() if domain else "general"
    clean = text

    # Strip LaTeX artifacts
    clean = re.sub(r"\$(.*?)\$", r"\1", clean)
    clean = clean.replace(r"\rightarrow", "→").replace(r"\leftarrow", "←")
    clean = re.sub(r"\\text\{([^}]+)\}", r"\1", clean)
    clean = re.sub(r"\\[a-zA-Z]+", "", clean)

    # Strip forbidden domain phrases
    if dom in ("se", "design"):
        clean = re.sub(r"(?i)\bpsychological\s+distance(s)?\b", "viewpoints", clean)
        clean = re.sub(r"(?i)\bfiltering\s+out\b", "missing from view", clean)
        clean = re.sub(r"(?i)\bmetacognitive\s+nudge\b", "structural check", clean)
        clean = re.sub(r"(?i)\bmetacognitive\s+pause\b", "system pause", clean)
        clean = re.sub(r"(?i)\bmetacognitive\b", "analytic", clean)
        clean = re.sub(r"(?i)\btherapeutic\b", "collaborative", clean)
        clean = re.sub(r"(?i)\binner\s+feeling(s)?\b", "observed signal", clean)
        clean = re.sub(r"(?i)\bemotional\s+charge\b", "assumed friction", clean)

    elif dom == "leadership":
        clean = re.sub(r"(?i)\bpsychological\s+distance(s)?\b", "organizational perspectives", clean)
        clean = re.sub(r"(?i)\btelemetry\s+trace(s)?\b", "decision trail", clean)
        clean = re.sub(r"(?i)\bempty\s+state\s+prototype\b", "unclear proposal", clean)

    return clean


def is_tooling_or_build(text: str) -> bool:
    """Helper identifying tooling, scripting, hardware, or build-vs-buy problem cues."""
    t = text.lower()
    return any(k in t for k in ["code", "vibe", "app", "software", "scan", "scanner", "driver", "kodak", "buy", "build", "script", "tool", "expensive", "costly"])


def is_infra_telemetry(text: str) -> bool:
    """Helper identifying infrastructure, latency, SRE, and telemetry problem cues."""
    t = text.lower()
    return any(k in t for k in ["p95", "p99", "latency", "replica", "queue", "database", "deadlock", "timeout", "pagerduty", "grafana", "telemetry"])


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
    def route_base_question(detection: DetectionNode, domain: str = "general", blend_with: Optional[str] = None) -> QuestionNode:
        """Emits the base (Cycle 0) Socratic Question for a detection."""
        intent, template_id, template_str = PATTERN_ROUTER_TABLE.get(
            detection.pattern,
            (
                SocraticIntent.CLARIFICATION,
                "generic_clarify_1",
                "When you say '[surface]', what specifically do you mean?",
            ),
        )

        framing = select_framing(domain, intent, blend_with=blend_with)
        question_text = template_str.replace("[surface]", detection.surface)

        surface_lower = detection.surface.lower()
        if any(k in surface_lower for k in ["phone", "battery", "monitor", "screen", "ram", "ssd", "hardware", "desk", "fan"]):
            intent = SocraticIntent.CLARIFICATION
            framing = "Let's check the observable device symptoms and pre-flight constraints."
            question_text = f"For '{detection.surface}', what specific symptoms, degradation, or observations prompted this repair or setup before you begin?"
        elif domain == "se":
            if is_tooling_or_build(surface_lower):
                if detection.pattern in (PatternType.CAUSE_EFFECT, PatternType.COMPARATIVE_DELETION, PatternType.MODAL_NECESSITY):
                    intent = SocraticIntent.PROBE_ALTERNATIVE
                    framing = "Let's inspect the build-versus-buy trade-offs before writing code."
                    if "expensive" in surface_lower or "costly" in surface_lower:
                        question_text = "Before building custom software because commercial tools are expensive, have you tested existing free utilities or open-source drivers (like NAPS2, native Kodak capture, or Apple Image Capture) for that hardware?"
                    else:
                        question_text = f"Before writing custom software for '{detection.surface}', have you tested existing free utilities or open-source drivers (like NAPS2, native Kodak capture, or Apple Image Capture) for that hardware?"

        return QuestionNode(
            targets_detection_id=detection.id,
            template_id=template_id,
            socratic_intent=intent,
            framing_string=framing,
            text=question_text,
            style="socratic",
            deepen_cycle=0,
            technique=None,
            domain=domain,
            blend_with=blend_with,
        )

    @staticmethod
    def route_deepening_question(
        detection: DetectionNode, current_cycle: int, last_answer: str, domain: str = "general", blend_with: Optional[str] = None
    ) -> QuestionNode:
        """Escalates through the per-pattern deepening ladder (Cycle 1 or 2) with domain grounding."""
        intent, template_id, _ = PATTERN_ROUTER_TABLE.get(
            detection.pattern,
            (SocraticIntent.CLARIFICATION, "generic_clarify_1", ""),
        )

        technique = DeepeningTechnique.EVIDENCE_LADDER
        text = ""

        if domain == "se":
            surface_lower = detection.surface.lower()
            ans_lower = last_answer.lower()
            is_tooling_or_build = any(
                k in surface_lower or k in ans_lower
                for k in ["code", "vibe", "app", "software", "scan", "scanner", "driver", "kodak", "buy", "build", "script", "tool", "hardware"]
            )

            if is_tooling_or_build:
                technique = DeepeningTechnique.EVIDENCE_LADDER
                intent = SocraticIntent.PROBE_ALTERNATIVE
                framing = "Let's check the build-versus-buy boundary before writing code."
                text = "Before writing custom software, what have you already tested with existing free utilities or open-source drivers (like NAPS2, Kodak native capture, or Apple Image Capture) for that hardware?"

            elif detection.pattern == PatternType.MIND_READING:
                if current_cycle == 1:
                    technique = DeepeningTechnique.OBSERVATION_SPLIT
                    framing = "Let's separate what the telemetry shows from the conclusion."
                    text = "Literally — what was the exact metric spike, log entry, or statement? And what did you infer on top of it?"
                else:
                    technique = DeepeningTechnique.METACOGNITIVE_NUDGE
                    framing = "We landed on that quickly."
                    text = "We landed on that very quickly — is that the complete service behavior, or is there a dependency we haven't traced yet?"
            elif detection.pattern == PatternType.CAUSE_EFFECT:
                if current_cycle == 1:
                    technique = DeepeningTechnique.EVIDENCE_LADDER
                    framing = "Let's inspect the causal mechanism in the pipeline."
                    text = f"If you point to the exact event that links '{detection.surface}' to that failure — what happened right before it?"
                else:
                    technique = DeepeningTechnique.TEMPORAL_PROBE
                    framing = "Tracing the timeline."
                    text = "Did the latency spike hit instantly under load, or did it queue up over time as connections pooled?"
            else:
                if current_cycle == 1:
                    technique = DeepeningTechnique.EVIDENCE_LADDER
                    framing = "Descend to a concrete trace or metric."
                    text = "If you had to pick one single concrete load test or trace that illustrates this — what happened?"
                else:
                    technique = DeepeningTechnique.METACOGNITIVE_NUDGE
                    framing = "Testing the assumption."
                    text = "We landed on 'that's it' very quickly — is that the complete trace, or the easiest explanation?"

        elif domain == "design":
            if detection.pattern == PatternType.MIND_READING:
                if current_cycle == 1:
                    technique = DeepeningTechnique.OBSERVATION_SPLIT
                    framing = "Let's separate user actions from our assumptions about their intent."
                    text = "Literally — what was the exact step where users dropped off? And what motivation are we assigning to them?"
                else:
                    technique = DeepeningTechnique.METACOGNITIVE_NUDGE
                    framing = "We landed on that quickly."
                    text = "We landed on that very quickly — is that verified by usability session replays, or our own intuition?"
            else:
                if current_cycle == 1:
                    technique = DeepeningTechnique.EVIDENCE_LADDER
                    framing = "Descend to a concrete user session."
                    text = "If you had to pick one single user session or prototype test that illustrates this — what happened?"
                else:
                    technique = DeepeningTechnique.METACOGNITIVE_NUDGE
                    framing = "Testing the usability assumption."
                    text = "We reached that conclusion quickly — does the click path data fully support that, or is there another friction point?"

        else:
            # Leadership / General default
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
                    framing = "Analytical pause."
                    text = "We landed on 'that's it' very quickly — is that the complete picture, or the easiest answer?"

        # Sanitize framing and text
        framing = sanitize_domain_output(framing, domain)
        text = sanitize_domain_output(text, domain)

        return QuestionNode(
            targets_detection_id=detection.id,
            template_id=f"{template_id}_deepen_{current_cycle}",
            socratic_intent=intent,
            framing_string=framing,
            text=text,
            style="socratic",
            deepen_cycle=current_cycle,
            technique=technique,
            domain=domain,
            blend_with=blend_with,
        )
