# 03_agent-system — Design Index

Build design for the Collaborative Thinking Partner. All decisions reflect the de-branded framing from `02_map/VERIFICATION.md` (no "NLP"/"Bandler" in user-facing copy; positioned as a structured problem-clarification engine).

| File | Role | Status |
|---|---|---|
| `architecture.md` | Top-level: components, Problem Graph data model (the core invention), GCP/ADK build plan, differentiators | Updated 2026-08-28 — adds §2.5 Socratic Layer + `question` node now `deepen_cycle`/`technique` |
| `state-machine.md` | 5-phase state machine (S1–S6), transition table, detection priority, **deepening sub-loop (S2, max 2 cycles)** | Updated 2026-08-28 |
| `classifier.md` | Meta-Model 11-pattern catalogue + deterministic router + confidence gating + Socratic Generation Layer + Deepening | Updated 2026-08-28 |
| `socratic-layer.md` | **Source of truth** for Socratic messaging: 11 patterns → 8 Paul-Elder moves, templates, voice rules, bedrock framing (§5), **deepening protocol (§7)** | Created 2026-08-28, deepening added |
| `system-prompts.md` | Orchestrator / phase / guardrail prompts — Socratic + empathic, one question/turn, **deepening voice rule** | Updated 2026-08-28 |
| `demo-script.md` | Professional-framing demo (founder co-founder conflict) — Socratic + bedrock | Updated 2026-08-28 |
| `design-rationale.md` | User requirements, architectural decisions, quality benchmarks, and anti-pattern guards | Updated 2026-08-31 |
| `implementation-plan.md` | Complete 4-step engineering blueprint: Environment, Core Backend, Graph Persistence, Split-Pane Web UI | Created 2026-08-30 |
| `gcp-deployment-plan.md` | GCP Cloud Run deployment, Vertex AI integration, containerization, and video blueprint | Created 2026-08-31 |
| `validation-corpus.md` | Real HN/Reddit corpus checks + gap analysis (mind_reading) | — |
| `worked-example-leadership-delivery.md` | Worked example delivery walkthrough | — |
| `CRISIS.md` | 3-Tier Urgency vs Crisis Triage, sliding window, soft lock, and data minimization | Created 2026-08-31 |

**Archives (never delete, per user directive):** `../_archive/agent-system/2026-08-28_pre-socratic/`, `../_archive/agent-system/2026-08-28_pre-deepening/`, `../_archive/agent-system/2026-08-28_variant-b/`

**Status (2026-08-31):** Full production Python build complete and **deployed live to Google Cloud Run** (`us-central1`, Vertex AI integration active) at [https://collaborative-thinking-partner-508821610672.us-central1.run.app](https://collaborative-thinking-partner-508821610672.us-central1.run.app). 66/66 passing tests across classifier, socratic layer, state machine, graph store, ADR diffs, security injection, crisis triage, and E2E worked examples. Split-pane web UI and API fully verified in production.

