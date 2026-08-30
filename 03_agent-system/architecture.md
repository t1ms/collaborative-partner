# Collaborative Thinking Partner — System Architecture

## 0. Strategic framing (from VERIFICATION.md)
Do **not** lead with "NLP" or "Bandler." Position the system as a **structured problem-clarification engine**: a formal grammar for problem statements plus a deterministic question-routing engine. The intellectual lineage is real but reframed — Meta-Model ≈ Socratic questioning + CBT distortion catalogue; Well-Formed Outcomes ≈ goal-setting theory (Locke & Latham) + motivational interviewing; perceptual positions ≈ perspective-taking. Present the contested origins honestly only if asked; never center them.

## 1. Problem → solution shape
Users arrive with vague, distorted, or stuck problem statements ("I can't decide," "they never listen," "this is overwhelming"). The agent does **not** give advice. It debugs the *statement* — surfacing missing structure, asking one precision question at a time, and producing a well-formed, actionable outcome the user owns.

## 2. Visual Architecture Diagram
![System Architecture](architecture-diagram.png)

## 2.1 Component map
```
User ──▶ ADK Orchestrator Agent ──┬─▶ Gemini 3.7 Flash (classification + empathic generation)
                                  ├─▶ Deterministic Router (rule table & Paul-Elder moves)
                                  ├─▶ Problem Graph Store (Firestore / local JSON fallback)
                                  └─▶ Live ADR Mutation Canvas (Real-time unified git diffs)
```
- **ADK Orchestrator**: owns the 5-phase loop (`state-machine.md`). One question per turn.
- **Gemini 3.7 Flash**: (a) classify incoming utterance into Meta-Model detection(s); (b) generate fluid Socratic question with conversational brevity dial (CARE 2026 / EMMI 2024).
- **Deterministic Router**: maps a detection type → `socratic_intent` + `template_id` + `framing_string`. This is the auditable "proof of work" — every question is traceable to a rule, not a black box.
- **Problem Graph Store**: persistent Problem Graph (§3). Survives turns and sessions. Feeds the visible UI trace and ADR canvas.

## 2.5 Socratic Messaging Layer
The agent's voice is **Socratic in method, empathic in tone** (user directive 2026-08-28): the user must feel accompanied and acknowledged while the reasoning is rigorously debugged. A framing vocabulary ("bedrock / descend") orients the user explicitly to the descent toward the load-bearing assumption — no mystery about the process. Full spec in `socratic-layer.md`; the pattern→intent map is summarized in `classifier.md`. The bedrock metaphor is user-facing and explicit.

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
