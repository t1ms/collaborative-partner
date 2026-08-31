"""Data models and schema definitions for the Collaborative Thinking Partner Problem Graph."""

from enum import Enum
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field
import time
import uuid


class PatternType(str, Enum):
    SIMPLE_DELETION = "simple_deletion"
    COMPARATIVE_DELETION = "comparative_deletion"
    UNSPECIFIED_REFERENT = "unspecified_referent"
    UNSPECIFIED_VERB = "unspecified_verb"
    CAUSE_EFFECT = "cause_effect"
    MIND_READING = "mind_reading"
    COMPLEX_EQUIVALENCE = "complex_equivalence"
    LOST_PERFORMATIVE = "lost_performative"
    UNIVERSAL_QUANTIFIER = "universal_quantifier"
    MODAL_NECESSITY = "modal_necessity"
    MODAL_POSSIBILITY = "modal_possibility"
    META_FRAME = "meta_frame"


class SocraticIntent(str, Enum):
    CLARIFICATION = "clarification"
    PROBE_ASSUMPTION = "probe-assumption"
    PROBE_EVIDENCE = "probe-evidence"
    PROBE_IMPLICATION = "probe-implication"
    PROBE_ALTERNATIVE = "probe-alternative"
    PROBE_VIEWPOINT = "probe-viewpoint"
    PROBE_CONCEPT = "probe-concept"
    META_COGNITION = "meta-cognition"
    PROBE_CRITERIA = "probe-criteria"
    PROBE_CAUSAL_LINK = "probe-causal-link"
    PROBE_EQUATION = "probe-equation"
    PROBE_SOURCE = "probe-source"
    PROBE_BARRIER = "probe-barrier"


class LayerType(str, Enum):
    UPSTREAM_STATE = "upstream_state"
    DOWNSTREAM_SYMPTOM = "downstream_symptom"


class StatePhase(str, Enum):
    S0_IDLE = "S0_IDLE"
    S1_INGEST = "S1_INGEST"
    S2_CLARIFY = "S2_CLARIFY"
    S3_OUTCOME = "S3_OUTCOME"
    S4_ANGLE = "S4_ANGLE"
    S5_ECOLOGY = "S5_ECOLOGY"
    S6_DONE = "S6_DONE"


class PhaseAction(str, Enum):
    STAY = "stay"
    ADVANCE = "advance"
    SKIP_NEXT = "skip_next"


class LLMTurnRecommendation(BaseModel):
    response_text: str = Field(description="Contextual Socratic response text to the user")
    socratic_intent: SocraticIntent = Field(default=SocraticIntent.CLARIFICATION, description="Primary Socratic intent")
    phase_action: PhaseAction = Field(default=PhaseAction.STAY, description="Recommended state machine action")
    phase_reason: str = Field(default="", description="Rationale for recommended phase transition or staying")
    detected_insight: Optional[str] = Field(default=None, description="Key extracted problem insight or root cause")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in transition recommendation")


class DeepeningTechnique(str, Enum):
    OBSERVATION_SPLIT = "observation_split"
    EVIDENCE_LADDER = "evidence_ladder"
    TEMPORAL_PROBE = "temporal_probe"
    THIRD_POSITION = "third_position"
    POSITIVE_INTENT = "positive_intent"
    METACOGNITIVE_NUDGE = "metacognitive_nudge"
    STAY_WITH = "stay_with"


class UtteranceNode(BaseModel):
    id: str = Field(default_factory=lambda: f"utt_{uuid.uuid4().hex[:8]}")
    text: str
    speaker: Literal["user", "agent"] = "user"
    timestamp: float = Field(default_factory=time.time)


class DetectionNode(BaseModel):
    id: str = Field(default_factory=lambda: f"det_{uuid.uuid4().hex[:8]}")
    utterance_id: str
    pattern: PatternType
    span: List[int] = Field(default_factory=lambda: [0, 0])  # [start_char, end_char]
    surface: str  # verbatim phrase
    confidence: float = 1.0
    layer: LayerType = LayerType.DOWNSTREAM_SYMPTOM
    domain_hint: Optional[str] = None
    domain_confidence: Optional[float] = None
    resolved: bool = False
    resolved_by_answer_id: Optional[str] = None
    deepen_count: int = 0
    created_at: float = Field(default_factory=time.time)


class QuestionNode(BaseModel):
    id: str = Field(default_factory=lambda: f"q_{uuid.uuid4().hex[:8]}")
    targets_detection_id: Optional[str] = None
    template_id: str
    socratic_intent: SocraticIntent
    framing_string: str
    text: str  # clean markdown text, no LaTeX
    style: str = "socratic"
    deepen_cycle: int = 0  # 0: base question, 1..2: deepening descents
    technique: Optional[DeepeningTechnique] = None
    domain: Optional[str] = None
    blend_with: Optional[str] = None
    created_at: float = Field(default_factory=time.time)


class AnswerNode(BaseModel):
    id: str = Field(default_factory=lambda: f"ans_{uuid.uuid4().hex[:8]}")
    question_id: str
    text: str
    is_closure: bool = False
    resolves_detection: bool = False
    created_at: float = Field(default_factory=time.time)


class OutcomePredicateKey(str, Enum):
    POSITIVE = "positive"
    SELF_INITIATED = "self_initiated"
    SENSORY = "sensory"
    CHUNK = "chunk"
    ECOLOGY = "ecology"


class OutcomePredicateNode(BaseModel):
    id: str = Field(default_factory=lambda: f"wfo_{uuid.uuid4().hex[:8]}")
    key: OutcomePredicateKey
    status: Literal["missing", "drafted", "verified"] = "missing"
    statement: str = ""
    evidence: str = ""
    updated_at: float = Field(default_factory=time.time)


class PerspectiveNode(BaseModel):
    id: str = Field(default_factory=lambda: f"persp_{uuid.uuid4().hex[:8]}")
    position: Literal["1st", "2nd", "3rd", "systemic", "reframe"]
    title: str
    content: str
    created_at: float = Field(default_factory=time.time)


class ConstraintNode(BaseModel):
    id: str = Field(default_factory=lambda: f"const_{uuid.uuid4().hex[:8]}")
    text: str
    severity: Literal["low", "medium", "critical"] = "medium"
    layer: LayerType = LayerType.DOWNSTREAM_SYMPTOM
    positive_intent: Optional[str] = None
    created_at: float = Field(default_factory=time.time)


class ArtifactVersion(BaseModel):
    id: str = Field(default_factory=lambda: f"art_{uuid.uuid4().hex[:8]}")
    version: int = 1
    title: str = "Problem Architecture Decision Record (ADR)"
    content: str  # Markdown ADR / Canvas
    diff: str = ""  # diff from previous version
    trigger_node_id: Optional[str] = None
    domain: str = "general"
    created_at: float = Field(default_factory=time.time)


class TasteProfile(BaseModel):
    user_id: str = "default_user"
    depth_preference: Literal["shallow", "balanced", "first_principles"] = "first_principles"
    vocabulary_tier: Literal["accessible", "executive", "technical"] = "executive"
    framing_anchor: Literal["bedrock", "complexity_debt", "five_whys"] = "bedrock"
    sessions_completed: int = 0
    updated_at: float = Field(default_factory=time.time)


class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    edge_type: Literal[
        "utterance->detection",
        "detection->question",
        "question->answer",
        "answer->resolution",
        "detection->outcome",
        "upstream->downstream",
        "perspective->root",
    ]


class ProblemGraph(BaseModel):
    session_id: str = Field(default_factory=lambda: f"ses_{uuid.uuid4().hex[:8]}")
    current_phase: StatePhase = StatePhase.S0_IDLE
    current_domain: str = "general"
    domain_history: List[str] = Field(default_factory=list)
    blend_with: Optional[str] = None
    utterances: List[UtteranceNode] = Field(default_factory=list)
    detections: List[DetectionNode] = Field(default_factory=list)
    questions: List[QuestionNode] = Field(default_factory=list)
    answers: List[AnswerNode] = Field(default_factory=list)
    outcome_predicates: Dict[OutcomePredicateKey, OutcomePredicateNode] = Field(default_factory=dict)
    perspectives: List[PerspectiveNode] = Field(default_factory=list)
    constraints: List[ConstraintNode] = Field(default_factory=list)
    artifacts: List[ArtifactVersion] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    active_detection_id: Optional[str] = None
    taste_profile: TasteProfile = Field(default_factory=TasteProfile)
    phase_turn_counts: Dict[str, int] = Field(default_factory=dict)
    phase_history: List[str] = Field(default_factory=list)
    novelty_history: List[float] = Field(default_factory=list)
    total_output_tokens: int = 0
    turn_timestamps: List[float] = Field(default_factory=list)
    crisis_lock_turns: int = 0
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

