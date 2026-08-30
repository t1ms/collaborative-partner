# Judging Criteria Mapping — Collaborative Partner (All Things Agentic)

> **Track:** Collaborative Partner — judged on *how the agent collaborates*, not domain.
> **Scoring:** Innovation & Operational Utility 40% + Architectural Discipline 30% + Demo & Production Readiness 30% = 5.0; Bonus up to +1.0 (public post +0.2, social +0.2, multi-model +0.2 each max 0.6) → 6.0. Deadline Aug 31 5pm PDT = Sep 1 00:00 UTC / 12:00 NZST.

## 1. The Three Pillar Requirements (Collaborative Partner)

| Pillar | What judges check (verbatim) | How we score | Evidence in repo |
|---|---|---|---|
| **1 — Interactive Guidance & Adaptation**<br>*Leads, guides step-by-step, captures feedback, adapts to thinking style* | Does agent proactively guide vs wait passively? Does it break down problems, ask clarifying Qs, capture preference feedback and adapt? | **S0→S6 5-phase loop enforces leading** — never passive. One-question/turn + empathic acknowledgement (bedrock/descend framing) + priority `cause_effect / mind_reading / complex_equivalence` first → auditable `pattern→intent→template` triple (immutable). Double-closure (`"I don't know"` → 2-cycle deepening max 2, `deepen_cycle`/`technique` logged) digs past shallow closures. Cross-session adaptation via `taste_profile {depth, vocab, framing}` loaded at S0 (mem0 pattern) → next session asks differently. | `state-machine.md` (S0-S6, S2 ladder), `classifier.md` (11 patterns), `socratic-layer.md` §2/§7, `system-prompts.md`, `architecture.md` §2-§3, `worked-example-leadership.md` Variant B, `code/firestore/taste.py` (planned) |
| **2 — Active Data Synthesis & Mutation**<br>*Not just reading data* | Does agent **synthesize/mutate** data vs just read? Did team ingest **messy/unstructured** streams? | **Live artifact mutation:** every resolved detection → `artifact_version {version, diff}` linked to `detection_id` — ADR block / canvas shape mutates in real time (right pane). Built via ADK tool `mutate_artifact` + CRDT (`yjs` 22k★, `BlockNote` 10k★ `replaceBlock`, `tldraw` 50k★ Store, ref `open-canvas` 5.4k★ diff-arch, `CopilotKit` 37k★).<br>**Messy ingestion + grounding:** `ingest_source` ingests GitHub repo (repomix 28k★ packs repo→XML for Gemini long-context), Figma PNG (Figma-Context-MCP 15k★ → JSON), PDF (marker 39k★ / docling 65k★ → markdown, RAGFlow 89k★ cited RAG) → `source_context` node, next Socratic Q cites `file:line` (Cody pattern from `sourcegraph` 10k★). Domain-agnostic by design — SE or design both satisfy, but text-only input = trap. | `architecture.md` §3 (Problem Graph), `code/agent/tools/mutate_artifact.py`, `code/agent/tools/ingest_source.py`, `code/web/ArtifactPane.tsx`, `code/web/ProblemGraphTrace.tsx` (planned) |
| **3 — Self-Improvement & Managing Context**<br>*Data lifecycle, no context rot* | Does agent demonstrate data lifecycle management + autonomous self-improvement where feedback explicitly alters future turns? Does it avoid context rot? | **Lifecycle discipline:** Firestore Problem Graph is append-only lineage — immutable triple + `deepen_cycle`/`technique` + `source_context` citations, queryable, not prompt-stuffed. Survives restarts, deduped via fencing-token pattern (temporal/redisson).<br>**Learning loop:** S6 summary embedded via Vertex → `taste_profile` + `precedent_bank` (mem0 64k★ vector+graph, Zep/Graphiti temporal KG, LangGraph CheckpointSaver) → injected at next S0 `system_instructions`. Second session demonstrably shallower/deeper per preference — captured feedback alters behavior (judges' "explicitly alters" test). | `architecture.md` §3, `code/shared/lease_locker.py`, `code/shared/precedent_bank.py` (planned), `code/firestore/taste.py` |

## 2. Stage Two — Weighted Rubric (maps pillars to scores)

| Weighted axis | Our leverage | Evidence |
|---|---|---|
| **Innovation & Operational Utility 40%** | `vague→actionable` via formal grammar of problem statements + bedrock metaphor (trustworthy) + artifact mutates live (judges see friction eliminated) | `demo-script.md` (0:00 repo drop → 0:20 ADR mutates), `worked-example-leadership.md` |
| **Architectural Discipline & Tech Stack 30%** | Decoupled ADK tools (`classify`, `route`, `ask`, `record`, `mutate_artifact`, `ingest_source`), deterministic router vs Gemini guardrail, Firestore vector+taste, failure recovery (idempotency + fencing) | `architecture.md` §5, `code/agent/**`, `code/firestore/**` |
| **Demo & Production Readiness 30%** | ≤4min video: live split-pane (graph trace left, artifact right) + GCS/BigQuery/Cloud Run console proof, reproducible `README.md` with `demo_scenarios.sh` style, `architecture.svg` diagram-as-code (diagrams 42k★) + reveal.js 72k★ deck | `docs/architecture.svg`, `README.md`, `demo-script.md` |

## 3. Bonus Up To +1.0

| Bonus | Plan | Repo fuel |
|---|---|---|
| Public post +0.2 | Blog on de-branded Meta-Model → Socratic engine | — |
| Social +0.2 | `#AllThingsAgenticHackathon` post with Veo clip | — |
| Multi-model +0.2 each (max 0.6) | Single fork `vertex-ai-creative-studio` 1.1k★ proves Veo (+0.2) + Lyria (+0.2) + Imagen (+0.2) in one repo; Gemma 2B 5.7k★ separate edge +0.2 distinct | `GoogleCloudPlatform/vertex-ai-creative-studio`, `google-deepmind/gemma` |

## 4. The "Chatbot with Memory" Trap — Explicit Guard

> Judges: *Vector search / RAG alone = basic retrieval, not a Collaborative Partner.*

| Trap signal | Our anti-trap proof |
|---|---|
| RAG without mutation | Every answer produces a visible `artifact_version` diff + Firestore graph node append — mutation is the demo hook (0:20) |
| Memory without adaptation | `taste_profile` loaded at S0 changes next session questioning (depth/vocab/framing) — explicit before/after in demo (session 1 vs 2) |
| Passive chatbot | S0-S6 one-question ladder *leads*; priority pattern ensures we dig at highest-leverage distortion first |

## 5. Scientific Defensibility & Judging Risk Mitigation (unchanged)

If judges question the origin: we explicitly decoupled actionable linguistic patterns from 1970s neurolinguistic pseudoscience.

1. **Discredited elements purged:** Zero sensory predicate matching (PRS), zero eye-accessing cues (EAC), zero computational "brain reprogramming" metaphors (>70% empirical trial refutation documented in Witkowski 2010; Passmore 2018).
2. **Active cognitive mechanisms retained:** Meta-Model as CBT/ACT cognitive restructuring; Well-Formed Outcomes as goal-setting theory (Locke & Latham); Perceptual Positions as psychological distancing; Clean Language (David Grove) as unadulterated cognitive elicitation; Positive-Intent backward chaining (Core Transformation) for secondary-gain alignment.
3. **Empirical lineage:** Cites the modern derivative trajectory (Astill Wright et al. 2023; Gray & Bourke 2017) proving that isolated, structured cognitive protocols succeed where grand NLP theories failed.
- Product framing: *"A formal grammar of problem statements with a deterministic Socratic question-routing engine and persistent Problem Graph."*

---
*Patched 2026-08-30 — superseded version archived to `_archive/agent-system/2026-08-30_pre-collab-rubric-remap/judging-mapping.md`. Now aligned to official 3-pillar Collaborative Partner rubric.*
