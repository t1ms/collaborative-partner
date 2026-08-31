# Collaborative Thinking Partner — System Architecture

## 0. System Definition & Core Hypothesis
The **Collaborative Thinking Partner** is a formal grammar for problem statements paired with a deterministic Socratic question-routing engine and a live mutating Problem Graph.

Rather than acting as a generic conversational advisor, the system debugs the *logical and linguistic structure* of problem statements — identifying implicit assumptions, cognitive distortions, and missing predicates to guide the user toward a self-authored, Well-Formed Outcome.

*(Empirical grounding and lineage are detailed in [`02_map/VERIFICATION.md`](../02_map/VERIFICATION.md) and [`03_agent-system/design-rationale.md`](design-rationale.md)).*

## 1. Problem → Solution Shape
Users arrive with vague, distorted, or stuck problem statements (*"I can't decide,"* *"they never listen,"* *"this is overwhelming"*). The agent does **not** give advice or prescribe solutions. It debugs the *statement* — surfacing missing structure, asking one precision question at a time, and rendering a well-formed, actionable outcome the user owns.

## 2. Visual Architecture Diagram
![System Architecture](architecture-diagram.png)

## 2.1 Component map
```
User ──▶ ADK Orchestrator Agent ──┬─▶ Gemini 3.7 Flash (Structured turn generation + Phase recommendations)
                                  ├─▶ 6-Layer State Machine Engine (Deterministic guardrail veto & phase gates)
                                  ├─▶ Problem Graph Store (Firestore / local JSON fallback)
                                  └─▶ Live ADR Mutation Canvas (Real-time unified git diffs)
```
- **ADK Orchestrator**: Coordinates dialogue turns under **Route B (Moderate Control)** — prompting Gemini for structured JSON recommendations while delegating all transition verdicts to the State Machine.
- **Gemini 3.7 Flash**: (a) Semantic domain classification; (b) Context-enriched Socratic generation with phase objectives, accumulated problem state, and phase transition recommendations (`stay`, `advance`, `skip_next`).
- **6-Layer State Machine Engine**: Enforces turn budgets (S2: 1–5, S3: 1–3, S4: 0–2, S5: 1–2, S6: 1), mandatory phase gates (S2, S3, S5, S6 locked), disengagement pivots (experiential grounding on "idk"), anti-spiral braking (auto-advance on stalled novelty), domain sanitization, and deterministic fallback.
- **Problem Graph Store**: Persistent Problem Graph (§3). Survives turns and sessions. Feeds the visible UI trace and ADR canvas.

## 2.5 Socratic Messaging Layer
The agent's voice is **Socratic in method, collaborative in tone**: the user feels accompanied and acknowledged while reasoning is rigorously debugged. A framing vocabulary ("bedrock / descend") orients the user explicitly to the descent toward the load-bearing assumption.
- **Closure signals** (*"that's it"*, *"obviously"*) trigger S2 deepening descents across 2 cycles.
- **Disengagement signals** (*"idk"*, *"how would I know"*) trigger concrete experiential pivots in S4 and S5 to prevent superficial phase advancement.

## 3. The Problem Graph — the core invention
A persistent, queryable graph of the user's problem as it is debugged. This is the original design contribution (the paper gives decision logic but no data model — see `02_map/INDEX.md`).

**Node types**
| node | fields | created when |
|---|---|---|
| `utterance` | text, ts | user speaks |
| `detection` | pattern, span, surface, confidence, layer: 'upstream_state' \| 'downstream_symptom' | classifier hits |
| `question` | template_id, targets_detection, text, socratic_intent, framing_string, style: 'socratic', deepen_cycle?: 0..2, technique? | router emits (one base node + up to 2 deepen nodes per detection; see socratic-layer.md §7) |
| `answer` | text, resolves (bool) | user replies |
| `outcome_predicate` | key ∈ {positive, self_initiated, sensory, ecology, chunk}, status | phase 3 |
| `perspective` | position ∈ {1,2,3,systemic}, text | phase 4 |
| `constraint` / `cost` | text, severity, layer: 'upstream_state' \| 'downstream_symptom' | phase 5 |

**Edges**: utterance→detection; detection→question; question→answer; answer→detection(resolved); detection→outcome_predicate; perspective→root; **upstream_state→downstream_symptom** (causal dependency link).

### 3.5 Dual-Horizon Triage Architecture (Upstream Engine + Downstream Relief)
Complex problems rarely arrive in isolation; they present as **downstream acute symptoms** (e.g. guilt over phone scrolling, missing team standups, procrastination on email) driven by **upstream state depletion** (e.g. chronic exhaustion, unsustainable workload, boundary collapse, survival mode).
- **Rule of Dual Triage:** 
  1. **Immediate Downstream Relief (Triage):** Frame a realistic, low-friction micro-commitment so the user gains immediate behavioral traction and breathing room.
  2. **Upstream Bedrock Descent:** Never stop at the symptom. Once the immediate friction is stabilized, bridge back to the upstream engine: *"Now that we have a 10-minute container for tonight, let's explore what is draining that tank so completely before you even walk through the door."*
- **Safety / Cognitive Boundary:** We never diagnose clinical disorders or offer medical advice. We Socratic-debug the *operational habits, cognitive expectations, workload assumptions, and recovery boundaries* that govern the user's capacity.

**Firestore shape**: `sessions/{sid}/graph/{nid}`. Each node a doc. Enables: (1) live trace UI; (2) resumable sessions; (3) deterministic audit — a judge can replay exactly which rule fired.

## 4. Pipeline summary (detail: state-machine.md)
P1 Ingestion+Classify → P2 Clarify/Router → P3 Outcome Architecture → P4 Multi-angle → P5 Ecology. Each phase reads/writes the graph and may loop back.

## 5. GCP / ADK build plan
- `thinking_partner` ADK agent (Python SDK), custom orchestration per state-machine.
- Tools: `classify`, `route`, `ask`, `record`, `wfo_check`, `perspective`, `ecology_check` — each a thin wrapper persisting to Firestore.
- Gemini 3.5 Flash for classification (latency), Pro for generation (quality) — configurable.
- Firestore native serverless; no containers needed.
- (Optional) Vertex AI eval harness using `02_map/demo-dialogues.md` as gold cases.

## 6. Differentiators for the rubric
- **Agent Framework**: explicit state machine + tool-based decomposition.
- **Gemini**: used for both structured classification and open generation, with deterministic guardrails.
- **GCP**: Firestore persistence + serverless deploy.
- **Twist**: the live, auditable Problem Graph — turns "AI gives advice" into "AI makes your own thinking visible and debuggable."
