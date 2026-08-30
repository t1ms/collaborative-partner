# Collaborative Thinking Partner — Core Engine (`src/`)

This directory contains the production Python backend, ADK 2 multi-agent orchestrator, Socratic reasoning layer, and split-pane web UI.

---

## 🏛️ Module Structure

```
src/thinking_partner/
├── agent/
│   ├── models.py          # Strongly typed Problem Graph schema (Pydantic v2)
│   ├── classifier.py      # 11 Meta-Model pattern catalogue & dual-horizon layer tagger
│   ├── socratic.py        # Paul-Elder 8-move router, deepening ladder & closure detector
│   ├── state_machine.py   # 5-phase deterministic state engine (S0..S6)
│   └── orchestrator.py    # Main turn coordinator connecting Gemini 3.7 Flash & rules
├── graph/
│   ├── store.py           # Problem Graph store (Firestore + local JSON fallback)
│   └── taste_bank.py      # Cross-session user taste profile & precedent bank
├── tools/
│   ├── mutate_artifact.py # Live ADR canvas generator emitting unified git diffs
│   └── ingest_source.py   # Unstructured document & repository ingestion tool
├── web/
│   ├── index.html         # Modern dark glassmorphic split-pane interface
│   ├── styles.css         # CSS tokens, Bedrock gauge, and diff styling
│   └── app.js             # Real-time SSE / REST dialogue & graph rendering logic
├── config.py              # GCP Project ID, Vertex AI, and model configurations
├── server.py              # FastAPI REST & Static file application
└── demo_scenarios.py      # Automated CLI scenario runner (Leadership Variant A & B)
```

---

## 🚀 Standalone Spin-Up

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Credentials (Optional)
```bash
export GEMINI_API_KEY="your-gemini-api-key"
# Or enable Vertex AI via Google Cloud ADC:
# export USE_VERTEX_AI=true
# export GCP_PROJECT_ID="your-project-id"
```
*(If no credentials are set, the system automatically runs in 100% deterministic offline mock mode).*

### 3. Launch Web Server
```bash
PYTHONPATH=src python3 -m uvicorn thinking_partner.server:app --reload --port 8000
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

### 4. Run CLI Scenario Runner
```bash
PYTHONPATH=src python3 -m thinking_partner.demo_scenarios
```

---

## 🧪 Running Tests
```bash
PYTHONPATH=src pytest tests/ -v
```
