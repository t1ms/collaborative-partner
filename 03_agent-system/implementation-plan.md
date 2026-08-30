# Collaborative Thinking Partner — System Implementation Plan (Steps 1–4)

## Architecture Overview
A production-ready implementation of the Collaborative Thinking Partner based on the `03_agent-system` specifications:
1. **Environment & GCP Configuration**: Python dependencies (`google-genai`, `fastapi`, `uvicorn`, `pydantic`, `pytest`, etc.), config loading for Gemini & Firestore.
2. **Core Agent Backend (`src/thinking_partner/agent/`)**:
   - `models.py`: Strongly typed Problem Graph nodes (Utterance, Detection, Question, Answer, OutcomePredicate, Perspective, Constraint, Artifact).
   - `classifier.py`: 11 Meta-Model pattern catalogue with dual-horizon layer tagging (`upstream_state` vs `downstream_symptom`), char spans, and confidence gating.
   - `socratic.py`: Paul-Elder 8-move taxonomy, deterministic router, base templates, bedrock/descend framing strings, closure-signal detector, and 2-cycle deepening ladder.
   - `state_machine.py`: S0_IDLE → S1_INGEST → S2_CLARIFY (with S2 deepening loop) → S3_OUTCOME → S4_ANGLE → S5_ECOLOGY → S6_DONE.
   - `orchestrator.py`: Empathic + Socratic turn shaping, clean language invariant, no-LaTeX invariant, and Gemini integration.
3. **Problem Graph Persistence & Tools (`src/thinking_partner/graph/`, `tools/`)**:
   - `store.py`: Problem Graph storage (Firestore native with resilient in-memory/JSON fallback for local zero-cloud runs).
   - `mutate_artifact.py`: Live ADR / Problem Canvas mutation engine emitting real-time diffs.
   - `taste_bank.py`: Cross-session taste profile & precedent bank for autonomous adaptation.
4. **Web UI & Live Split-Pane Demo (`src/thinking_partner/server.py`, `src/thinking_partner/web/`)**:
   - FastAPI server with REST/SSE endpoints.
   - Rich, modern split-pane UI: Socratic dialogue left, live mutating Problem Graph trace & ADR right with real-time badges (pattern, move, cycle, bedrock).
5. **Verification**:
   - Automated unit and integration tests (`tests/`).
   - E2E scenario run validating the leadership worked example trace (Variant A & B).
