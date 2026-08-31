"""Domain Overlay Loader and Pack Definitions.

Reads overlay specifications from 02_map/overlays/ and provides structured vocabulary,
framing angles, S4 perspective definitions, and forbidden phrase lists for each domain.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from ..config import OVERLAY_DIR, DOMAIN_MAX_DEEPEN, DOMAIN_ECOLOGY_CAPS


class DomainPack(BaseModel):
    domain: str
    title: str
    artifact_title: str
    keywords: List[str] = Field(default_factory=list)
    primary_observer: str = ""
    counterparty: str = ""
    evidence_sources: str = ""
    orientation_rationale: str = ""
    s4_perspectives: Dict[str, Tuple[str, str]] = Field(default_factory=dict)  # pos -> (title, content)
    forbidden: List[str] = Field(default_factory=list)
    vocab_summary: str = ""
    max_deepen: int = 2
    ecology_caps: int = 1


# Built-in fallback packs ensuring resilient operation
FALLBACK_PACKS: Dict[str, DomainPack] = {
    "se": DomainPack(
        domain="se",
        title="Software Engineering & SRE",
        artifact_title="Architecture Decision Record (ADR)",
        keywords=[
            "p95", "p99", "latency", "replica", "replicas", "pagerduty", "grafana",
            "checkout api", "queue", "queues", "3x load", "load test", "throughput",
            "rps", "database", "postgres", "redis", "kafka", "deadlock", "timeout",
            "retry", "failover", "bottleneck", "telemetry", "trace", "traces", "span",
            "oom", "memory leak", "cpu spike", "deploy", "incident", "sla", "slo",
            "rfc", "microservice", "cluster", "kubernetes", "k8s",
            "code", "vibe code", "script", "app", "software", "scanner", "driver",
            "hardware", "tooling", "build-vs-buy", "automation", "batch", "open source",
            "library", "cli", "sdk", "integration", "ocr", "api",
            "gcp", "cloud", "cloud run", "docker", "serverless", "devops", "upload", "backend", "infrastructure", "deploy", "deployment"
        ],
        primary_observer="SRE / telemetry observer with only metrics, traces, and black-box logs",
        counterparty="Downstream service caller or upstream dependencies with hard timeout contracts",
        evidence_sources="p95 dashboard panel, distributed trace waterfall, load test run, queue depth graph",
        orientation_rationale="Let's look at this purely from the service telemetry and queue dynamics.",
        s4_perspectives={
            "1st": ("Service Owner Perspective", "Operating as the service on-call managing resource limits, capacity, and SLO budgets."),
            "2nd": ("Downstream Caller Angle", "Seeing the contract from client services expecting low-latency response times without degradation."),
            "3rd": ("Telemetry & Black-Box Observer", "Viewing only exact timestamps, queue depth metrics, and distributed trace error codes."),
            "reframe": ("Systemic Bottleneck Reframe", "Treating latency not as bad code, but as unbuffered I/O or mismatched concurrency models."),
        },
        forbidden=[
            "psychological distance", "filtering out", "metacognitive label", "metacognitive",
            "emotional reaction", "inner feeling", "emotional charge", "therapeutic"
        ],
        vocab_summary="telemetry, traces, p95/p99 latency, queue depth, replica capacity, failover, SLA/SLO contracts, scanner drivers, spare capacity, build-vs-buy",
        max_deepen=DOMAIN_MAX_DEEPEN.get("se", 1),
        ecology_caps=DOMAIN_ECOLOGY_CAPS.get("se", 1),
    ),
    "design": DomainPack(
        domain="design",
        title="Product & UX Design",
        artifact_title="User Journey & Friction Canvas",
        keywords=[
            "user", "users", "onboarding", "figma", "journey", "drop-off", "drop off",
            "prototype", "empty state", "conversion", "churn", "ux", "ui", "friction",
            "click path", "usability", "modal", "affordance", "information architecture",
            "design system", "interaction", "mockup", "wireframe", "micro-copy", "flow",
            "signup", "bounce", "cognitive load"
        ],
        primary_observer="First-time user / support transcript / session replay evaluator",
        counterparty="Confused first-time user encountering the empty state or form error",
        evidence_sources="Task completion rate, drop-off funnel, click path replay, user testing video snippet",
        orientation_rationale="Let's look at this directly through the first-time user's journey and interaction friction.",
        s4_perspectives={
            "1st": ("Design Intent Perspective", "Orchestrating intuitive mental models, clear affordances, and zero-friction task flows."),
            "2nd": ("First-Time User Angle", "Encountering the interface without prior mental context or product familiarity."),
            "3rd": ("Session Replay & Funnel Observer", "Tracking mouse trajectories, hesitation pauses, and exact drop-off steps without assumptions."),
            "reframe": ("Interaction Affordance Reframe", "Treating user churn not as user mistake, but as an ambiguous visual affordance."),
        },
        forbidden=[
            "psychological distance", "filtering out", "metacognitive label", "metacognitive",
            "sre telemetry", "database lock", "server replica", "therapeutic"
        ],
        vocab_summary="user journey, onboarding flow, click path, drop-off funnel, visual affordance, empty state, cognitive load",
        max_deepen=DOMAIN_MAX_DEEPEN.get("design", 1),
        ecology_caps=DOMAIN_ECOLOGY_CAPS.get("design", 1),
    ),
    "leadership": DomainPack(
        domain="leadership",
        title="Leadership & Stakeholder Alignment",
        artifact_title="Strategic Outcome & Alignment Record (WFO)",
        keywords=[
            "team", "teams", "motivation", "ownership", "stakeholder", "stakeholders",
            "roadmap", "product pings", "director", "vp", "executive", "skip-level",
            "alignment", "headcount", "priority", "priorities", "1-on-1", "one-on-one",
            "review", "promotion", "delegation", "career", "cross-functional", "buy-in",
            "consensus", "politics", "sprint backlog", "delivery", "leadership material"
        ],
        primary_observer="Neutral skip-level leader or objective board observer evaluating decision clarity",
        counterparty="Cross-functional peer (Product/Sales/Exec) managing competing quarterly commitments",
        evidence_sources="Decision log, committed roadmap RFC, explicit 1-on-1 feedback, signed-off sprint backlog",
        orientation_rationale="Let's look at this through the lens of organizational alignment, stakeholder incentives, and decision ownership.",
        s4_perspectives={
            "1st": ("Direct Lead Perspective", "Managing team output, sustainable capacity, and high-leverage focus."),
            "2nd": ("Cross-Functional Stakeholder Angle", "Expecting predictable milestone delivery, de-risked commitments, and clear communication."),
            "3rd": ("Neutral Third-Party Observer", "Reviewing written commitments, decision logs, and concrete handoffs without politics."),
            "reframe": ("Incentive Alignment Reframe", "Treating resistance not as personal conflict, but as differing accountability metrics."),
        },
        forbidden=[
            "telemetry trace", "empty state prototype", "p95 latency", "psychological distance"
        ],
        vocab_summary="stakeholder alignment, decision ownership, roadmap commitments, sprint backlog, organizational incentives",
        max_deepen=DOMAIN_MAX_DEEPEN.get("leadership", 2),
        ecology_caps=DOMAIN_ECOLOGY_CAPS.get("leadership", 2),
    ),
    "general": DomainPack(
        domain="general",
        title="General Socratic Problem Clarification",
        artifact_title="Problem Architecture Record",
        keywords=["problem", "stuck", "confused", "frustrated", "decision", "overwhelmed", "challenge", "option", "goal", "situation", "friction"],
        primary_observer="Objective observer viewing only the observable sequence of events",
        counterparty="Counterparty experiencing the external effects of the situation",
        evidence_sources="Concrete observable actions, timestamped events, verifiable outcomes",
        orientation_rationale="Let's look at the observable facts and constraints underneath the situation.",
        s4_perspectives={
            "1st": ("Your Direct Perspective", "Operating from your core objectives with direct agency and realistic boundaries."),
            "2nd": ("Counterparty / Stakeholder Angle", "Seeing the interaction from their operational constraints, deadlines, and unstated pressures."),
            "3rd": ("Objective Observer (Fly on the Wall)", "Viewing the dynamic without emotional charge — evaluating only the verifiable facts and structural incentives."),
            "reframe": ("Cognitive Reframe", "Treating the perceived limitation not as an identity deficit, but as a lack of calibrated feedback mechanisms."),
        },
        forbidden=[],
        vocab_summary="observable facts, underlying constraints, concrete friction, practical tradeoffs",
        max_deepen=DOMAIN_MAX_DEEPEN.get("general", 2),
        ecology_caps=DOMAIN_ECOLOGY_CAPS.get("general", 1),
    ),
}

_LOADED_PACKS: Optional[Dict[str, DomainPack]] = None


def load_domain_packs(overlay_dir: Optional[Path] = None) -> Dict[str, DomainPack]:
    """Loads domain overlay markdown files or returns built-in fallback packs."""
    global _LOADED_PACKS
    if _LOADED_PACKS is not None:
        return _LOADED_PACKS

    target_dir = overlay_dir or OVERLAY_DIR
    packs = dict(FALLBACK_PACKS)

    if target_dir.exists() and target_dir.is_dir():
        for md_file in target_dir.glob("*.md"):
            domain_name = md_file.stem.lower()
            try:
                content = md_file.read_text(encoding="utf-8")
                # Parse markdown sections if available, merging on top of fallback
                base_pack = packs.get(domain_name, DomainPack(domain=domain_name, title=domain_name, artifact_title="Decision Record"))
                
                # Extract keywords if present
                if "## Trigger Keywords" in content:
                    kw_section = content.split("## Trigger Keywords")[1].split("##")[0]
                    kws = [w.strip().lower() for w in kw_section.replace("\n", ",").split(",") if w.strip()]
                    if kws:
                        base_pack.keywords = kws

                # Extract forbidden words
                if "## Forbidden for Domain" in content:
                    forb_section = content.split("## Forbidden for Domain")[1].split("##")[0]
                    forbs = [w.strip().lower() for w in forb_section.replace("\n", ",").split(",") if w.strip() and w.strip() != "(none)"]
                    if forbs:
                        base_pack.forbidden = forbs

                # Extract depth policy if present
                if "## Depth Policy" in content:
                    depth_section = content.split("## Depth Policy")[1].split("##")[0]
                    for line in depth_section.splitlines():
                        if "Max Deepen Cycles:" in line or "max_deepen" in line.lower():
                            m = re.search(r"(\d+)", line)
                            if m:
                                base_pack.max_deepen = int(m.group(1))
                        if "Ecology Caps:" in line or "ecology_caps" in line.lower():
                            m = re.search(r"(\d+)", line)
                            if m:
                                base_pack.ecology_caps = int(m.group(1))

                packs[domain_name] = base_pack
            except Exception:
                pass

    _LOADED_PACKS = packs
    return _LOADED_PACKS


def get_domain_pack(domain: str) -> DomainPack:
    """Retrieves the domain pack for the specified domain, defaulting to 'general'."""
    packs = load_domain_packs()
    return packs.get(domain.lower(), packs["general"])
