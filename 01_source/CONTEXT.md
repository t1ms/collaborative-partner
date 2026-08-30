# 01_source — Canonical Research & Technical Source Material

One job: hold the canonical source research papers, empirical validation references, conversational alliance research, and Google Cloud / ADK architectural engineering guides.

## Inputs
- None (this is the root source of truth).

Do NOT load: intermediate draft revisions or unverified online summaries.

## Process
1. Maintain read-only ground truth documents (all available as `.md`).
2. Read for extraction into `02_map/` (cognitive models & conversational dynamics) and reference during `03_agent-system/` (GCP/ADK implementation & generation parameters).

## Outputs

### 1. Research Corpus (`01_source/research/`)
*Full scientific lineage and empirical defensibility backing our agent architecture and conversational dial.*
- `research/bandler-nlp-thinking-partners.md` — Primary theoretical ontology: Meta-Model parsing, VAKOG submodal coding, TOTE feedback loops, and 5-phase pipeline.
- `research/NLP Derivatives and Empirical Validity.md` — Defensibility reference, scientific literature review, and de-branding taxonomy.
- `research/2024-EMMI-Empathic-Multimodal-MI.md` — EMMI Dataset (arXiv:2406.16478): Client-adaptive brevity; short reflections using the user's verbatim words drive the alliance.
- `research/2026-CARE-Therapeutic-Alliance-LLM.md` — CARE (arXiv:2602.20648): Turn-level working alliance prediction; verbose turns drop working alliance instantly, while rationale-augmented brevity recovers it.
- `research/2025-PST-MI-Caregivers-LLM.md` — PST+MI for Family Caregivers (arXiv:2506.11376): Few-Shot+RAG empathy tension ("thorough vs efficient") — brevity wins live collaborative engagement.
- `research/Transforming Discussion Language - Applying Marketing Communication Architecture to Interpersonal and Strategic Discourse.md` — Operational Inversion (leading with outcomes), Hayakawa's Ladder of Abstraction (vertical oscillation), and Two-Sided Inoculation.
- `research/README.md` — Canonical research index and traceability mapping.

### 2. Information Architecture & Cognitive Load Theory (`01_source/`)
*Grounds structural clarity, cognitive ergonomics, and agent experience.*
- `Theoretical Foundations, Structural Frameworks, and Operational Frontiers of Technical Communication.md` — Cognitive Load Theory (Sweller CLT), Information Mapping (Horn), Minimalist Instruction (Carroll), Diátaxis, arc42, C4, ADRs, ASD-STE100, and Agent Experience (AX).

### 3. Google Cloud & Hackathon Technical Architecture (`01_source/`)
*Grounds ADK 2 multi-agent orchestration, persistent state machines, self-improvement, and judging compliance.*
- `judging-criteria.md` — Live judging breakdown from DevRel (Christina Lin, Willie): Collaborative Partner track specifics (active mutation vs basic RAG), 4-min video blueprint, and GCP backend proof.
- `orchestration-google-adk.md` — ADK 2 Multi-Agent Orchestration patterns (Graph Workflows / `JoinNode`, Collaborative Teams / Concierge, Dynamic LLM-shaped workflows).
- `long-running-agent.md` — Persistent ADK workflows (`DatabaseSessionService`, `ResumabilityConfig`, `LongRunningFunctionTool`, Idempotency guards, Cloud Trace).
- `building-a-self-evolving-agent.md` — Autonomous self-improvement, `adk optimize`, trajectory-based evaluation vs "looks-complete" cheating, Vertex Gen AI Eval, Gemma fine-tuning traces.

## Human check
Verify that the files remain unaltered and treat them as ground truth for cognitive models in `02_map/` and technical implementation in `03_agent-system/`.
