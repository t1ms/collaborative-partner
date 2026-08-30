# Collaborative Thinking Partner — The Pipeline
 
The flow in one line: extract Bandlerian cognitive models from research, map them into deterministic agent modules, and design the production Socratic agent system for Gemini/GCP utilizing official Google ADK patterns and judging criteria.
 
| Stage | Job | Input | Output | Human check |
|---|---|---|---|---|
| `01_source` | Canonical research & GCP engineering store | Research papers & Google ADK guides | Domain papers (`bandler-nlp-*.pdf`, `NLP Derivatives...`) & GCP guides (`judging-criteria.md`, `orchestration-google-adk.md`, `long-running-agent.md`, `building-a-self-evolving-agent.md`) | Ground truth fidelity |
| `02_map` | Distill cognitive ontology | `01_source` | `02_map/*.md` (6 modules) | Models faithful to paper, de-branded |
| `03_agent-system` | Build Socratic agent architecture & GCP deployment | `02_map` modules & `01_source` GCP guides | `architecture.md`, `state-machine.md`, `system-prompts.md`, `worked-examples`, `judging-mapping.md` | Judging rubric alignment, GCP ADK fidelity, 2-cycle deepening |
 
Factory (stable, every run): `01_source/`, `02_map/`
Product (build & deliverables): `03_agent-system/`
Archive (cold storage): `_archive/` (historical design variants, prior iterations)
 
Status is whatever exists: a stage is COMPLETE when its outputs hold verified documentation and specs.

