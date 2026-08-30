# Collaborative Thinking Partner

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Google Gen AI](https://img.shields.io/badge/Model-Gemini_3.7_Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Tests](https://img.shields.io/badge/Tests-23%20Passed-brightgreen.svg)](#)
[![License](https://img.shields.io/badge/License-Apache_2.0_%2F_CC_BY_4.0-blue.svg)](LICENSE)

> **A Socratic Problem-Clarification Engine.**  
> Rather than offering generic advice or ungrounded solutions, the Thinking Partner debugs the *structure of problem statements* using formal cognitive grammar (11 Meta-Model patterns), 8 Paul-Elder Socratic moves, an empirical working alliance verbosity dial, and a live mutating Problem Graph.

---

## 🏛️ System Overview

![System Architecture](03_agent-system/architecture-diagram.png)

### How It Works

1. **Guided Socratic Descent**
   - **5-Phase State Machine (`S0_IDLE → S1_INGEST → S2_CLARIFY → S3_OUTCOME → S4_ANGLE → S5_ECOLOGY → S6_DONE`)** guarantees structured problem progression.
   - **2-Cycle Deepening Ladder**: Resists shallow closures (*"I don't know"*, *"that's all"*) by escalating through observation splits and metacognitive nudges to reveal load-bearing assumptions.
   - **Fluid Alliance Voice**: Calibrates turn-level length and reflection using working alliance principles* — synthesizing 2–3 sentence turns that pair verbatim reflection with a single crisp question.
   - **Ladder of Abstraction Navigation**: Oscillates vertically between high-level strategic intent and concrete ground-level moments without dead-level abstraction.

2. **Live Problem Canvas & Continuous Mutation**
   - **Architecture Decision Record (ADR) Canvas**: Dynamically mutates on every resolved detection with real-time unified diffs.
   - **Unstructured Source Grounding**: Ingests transcripts, design briefs, notes, and repository context via `ingest_source`.

3. **Cross-Session Depth Adaptation**
   - **Persistent Taste & Precedent Bank (`taste_bank.py`)**: Tracks depth and framing preferences across sessions without context rot or prompt stuffing.
   - **Trajectory-Based Verification**: Validates actual cognitive resolution before marking problem layers resolved.

*\*Tuned via empirical findings on therapeutic alliance and conversational verbosity (EMMI 2024, CARE 2026, PST-MI 2025).*

---

## 🚀 Quickstart

### 1. Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment (Google Cloud / Gemini)
Copy `.env.example` to `.env` and set your credentials:
```bash
cp .env.example .env
```
*(Supports both Google AI Studio `GEMINI_API_KEY` and Google Cloud Vertex AI ADC with `USE_VERTEX_AI=true`).*

### 3. Run the Automated Terminal Demo
```bash
PYTHONPATH=src python3 -m thinking_partner.demo_scenarios
```

### 4. Launch the Interactive Split-Pane Web UI
```bash
PYTHONPATH=src python3 -m uvicorn thinking_partner.server:app --reload --port 8000
```
Open **[http://localhost:8000](http://localhost:8000)** to view the live split-pane UI:
- **Left Pane:** Socratic dialogue with real-time badges (pattern, move, cycle, and Bedrock gauge).
- **Right Pane:** Live mutating ADR canvas, Problem Graph node tree, and audit diff inspector.

---

## 🧪 Testing

Run the full automated test suite (23/23 unit & integration tests):
```bash
PYTHONPATH=src pytest tests/ -v
```

---

## 📂 Repository Layout (ICM)

- `01_source/` — Canonical research corpus (searchable Markdown `.md` papers), empirical validity references, and Google Cloud ADK architecture guides.
- `02_map/` — Distilled cognitive models, conversational dynamics (alliance dial), and de-branding protocols.
- `03_agent-system/` — Architecture design specifications, worked examples, implementation plan, and design rationale.
- `src/thinking_partner/` — Production Python backend, orchestrator, deterministic classifier, Socratic router, and web UI.
- `tests/` — Automated test suite reproducing gold-standard evaluation dialogues.

---

## 📚 Acknowledgements & Scientific Lineage

This project builds on established cognitive science, linguistic modeling, empirical conversational research, and Google Cloud ADK multi-agent architecture. We give full credit to the foundational authors and researchers:

### 1. Cognitive Architecture & Linguistic Deconstruction
- **Bandler & Grinder (1975)** — *The Structure of Magic I & II*: Foundational Meta-Model linguistic distortion taxonomy (Deletions, Distortions, Generalizations).
- **Miller, Galanter, & Pribram (1960)** — *Plans and the Structure of Behavior*: TOTE (Test-Operate-Test-Exit) cybernetic feedback loops.
- **Robert Dilts (1999)** — *Sleight of Mouth: The Magic of Conversational Belief Change*: Semantic reframing patterns and Meta-Mirror (4th systemic perceptual position, 1988–1992).
- **Grinder & DeLozier (1987)** — *Turtles All the Way Down*: 1st, 2nd, and 3rd Perceptual Positions.
- **Leslie Cameron-Bandler (1978)** — *They Lived Happily Ever After*: Codification of Positive Intent, outcome questioning, and reframing sequences.

### 2. Empirical Validation & De-Branding
- **Witkowski (2010), Passmore & Rowson (2018), Sturt et al. (2012)**: Empirical meta-analyses establishing the boundary between valid linguistic inquiry and unverified pseudoscience (documented in [`02_map/VERIFICATION.md`](02_map/VERIFICATION.md)).
- **David Grove**: Clean Language methodology (verbatim user word reuse without outside metaphor contamination).
- **Locke & Latham (1990/2002)**: Goal-Setting Theory underpinning Well-Formed Outcome (WFO) testable exit conditions.
- **Paul & Elder (2006)** — *Critical Thinking: Tools for Taking Charge of Your Learning and Your Life*: 8-move Socratic Taxonomy for rigorous intellectual inquiry.

### 3. Conversational Alliance & Verbosity Science
- **EMMI (2024)** — Galland, Pelachaud, & Pecune ([arXiv:2406.16478](https://arxiv.org/abs/2406.16478)): Verbatim reflections & client-adaptive brevity in motivational dialogue.
- **CARE (2026)** — Li, Wang, Lu, Xu, Ma, & Lan ([arXiv:2602.20648](https://arxiv.org/abs/2602.20648)): Computational working alliance prediction & rationale-augmented brevity.
- **PST+MI for Caregivers (2025)** — Wang et al. ([arXiv:2506.11376](https://arxiv.org/abs/2506.11376)): In-context learning for Problem-Solving Therapy and resolving the thoroughness vs. efficiency tension.
- **Grice (1975)**: Maxim of Quantity (*Logic and Conversation*).
- **Sweller (1988)**: Cognitive Load Theory (CLT).
- **Hayakawa (1939/1949)**: *Language in Thought and Action* (The Ladder of Abstraction).
- **Carroll (1990)**: *The Nurnberg Funnel* (Minimalist Instruction).

### 4. Google Cloud & ADK Multi-Agent Architecture
- **Annie Wang, Christina Lin, & Romin Irani**: *Architecting Multi-Agent Teams: Mastering ADK 2* (Graph workflows, Concierge patterns, and Dynamic agent routing).
- **Christina Lin, Willie, & Darliss Call**: Google Cloud "All Things Agentic" DevRel Workshops & agentic architecture guidance.

### 5. Repository Architecture & Knowledge Methodology
- **Interpretable Context Methodology (ICM)**: The repository and agent knowledge workspace are architected using ICM conventions (*folders carry sequencing, hierarchy carries context, files carry state*), establishing verifiable stage gates (`01_source/` $\rightarrow$ `02_map/` $\rightarrow$ `03_agent-system/`) for human-in-the-loop agent reasoning and complete auditability.

---

## 📖 How to Cite This Work

If you build upon this architecture or reference our Socratic Problem-Clarification state machine, please cite this work:

```bibtex
@misc{collaborative_thinking_partner_2026,
  title={Collaborative Thinking Partner: A Socratic Problem-Clarification Engine with Dual-Horizon Triage and Live Architecture Decision Record Mutation},
  author={Collaborative Thinking Partner Contributors},
  year={2026},
  howpublished={\url{https://github.com/t1ms/collaborative-partner}},
  note={Built for the Google Cloud All Things Agentic Hackathon}
}
```

*Originally developed for the Google Cloud "All Things Agentic" Hackathon — an open-source Socratic problem-clarification engine.*
