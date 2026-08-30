# 03_agent-system — Agent Architecture & Build Design

One job: implement the Socratic thinking partner architecture, state machine, prompt engineering, and worked evaluation traces for the hackathon build.

## Inputs
- Working: None (generates build artifacts).
- Reference: `../02_map/*.md` (the distilled cognitive ontology).

Do NOT load: prior unverified draft revisions. (Consult `../_archive/agent-system/` only if historical comparison is requested).

## Process
1. Architect the multi-phase state machine (S1–S6) with 2-cycle Socratic deepening loops.
2. Build the deterministic classifier and Socratic translation layer (Paul-Elder questions).
3. Draft system prompts ensuring empathic acknowledgment and strict single-question turns.
4. Validate against real-world test corpora (`_hn_raw.json`, `_reddit_raw.json`) and document worked examples.
5. Non-overwrite rule: when revising architecture or prompts, move superseded files to `../_archive/agent-system/` before writing new versions.

## Outputs
- `architecture.md` — Full system components and Problem Graph schema.
- `state-machine.md` — 5-phase transition logic and S2 deepening loops.
- `classifier.md` — 11 Meta-Model pattern definitions and confidence scoring.
- `socratic-layer.md` — Paul-Elder question mapping and bedrock framing.
- `system-prompts.md` — Orchestrator and phase execution prompts.
- `demo-script.md` & `worked-example-leadership.md` — End-to-end evaluation traces.
- `judging-mapping.md` — Hackathon rubric alignment matrix.
- `INDEX.md` — Design index and build status.

## Human check
Verify that the design answers what a hackathon judge will score, ensures non-advice-giving cognitive debugging, and aligns with the Google Agentic stack (Gemini / ADK).
