# Collaborative Thinking Partner

AI Thinking Partner built for the Google "All Things Agentic" hackathon. Helps users work through complex problems using structured cognitive models (Meta-Model, Well-Formed Outcomes, Socratic Deepening) rather than generic advice.

Built on ICM: folders carry sequencing, hierarchy carries context, files carry state.

## Where things live

| Folder | What it holds |
|---|---|
| `01_source/` | Canonical research papers, empirical validity references, and Google Cloud ADK architecture guides |
| `02_map/` | Distilled cognitive models, taxonomies, and verification protocols |
| `03_agent-system/` | Agent architecture, state machine, Socratic layer, prompts, and worked examples |
| `_templates/` | Blank starters for new map modules and worked examples |
| `_archive/` | Cold storage for superseded drafts, early design variants, and raw scrapes |

## Route by what just happened

| If | Go to | Then stop at |
|---|---|---|
| inspecting source papers | `01_source/CONTEXT.md` | read canonical materials |
| mapping research to models | `02_map/CONTEXT.md` | human verifies against paper |
| designing/building agent | `03_agent-system/CONTEXT.md` | human checks design alignment |
| modifying existing design files | create new version or move previous to `_archive/` | verify active file |
| referencing past design variants | check `_archive/agent-system/` | return with context to active work |
| configuring / deploying to GCP | `01_source/GCP.md` | pre-flight verification & runbook |
| asked for status | scan `03_agent-system/INDEX.md` | report current build state |

## Rules

1. **Human Gate:** Nothing moves forward until a person has verified the output of the current stage against the source and rubric.
2. **Non-Overwrite Archival:** Never overwrite or delete superseded designs destructively. Move replaced iterations into `_archive/<category>/`.
3. **Plain Text as State:** Keep models, prompts, and dialogue traces in linkable markdown with clear references.
