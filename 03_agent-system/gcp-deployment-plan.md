# Google Cloud Platform (GCP) Implementation & Deployment Plan

> **Objective:** Deploy the Collaborative Thinking Partner to Google Cloud Run with Vertex AI (Gemini 3.7 Flash) integration, serverless autoscaling, persistent session graph persistence, and Cloud Logging telemetry for hackathon submission proof.

---

## 🏛️ GCP Architecture Map

```
                                  ┌────────────────────────────────────────────────────────┐
                                  │               Google Cloud Platform (GCP)              │
                                  │                                                        │
[ End User / Judges ] ───────────▶│  Google Cloud Run (Serverless Container - Port 8080)  │
      (HTTPS Web UI)              │  - FastAPI REST & SSE Endpoints                        │
                                  │  - Split-Pane Socratic Dialogue UI                     │
                                  │  - In-Memory / Firestore State Machine Engine          │
                                  └───────────────┬───────────────────────┬────────────────┘
                                                  │                       │
                                                  ▼                       ▼
                                       ┌─────────────────────┐ ┌─────────────────────┐
                                       │ Vertex AI Platform  │ │    Cloud Logging    │
                                       │ - Gemini 3.7 Flash  │ │ - Session Telemetry │
                                       │ - Gen AI Evaluation │ │ - Graph Audit Trail │
                                       └─────────────────────┘ └─────────────────────┘
```

---

## 📋 4-Phase GCP Execution Plan

### Phase 1: Environment & Cloud API Activation
Enable the required Google Cloud APIs for Vertex AI reasoning, Cloud Run container hosting, and Cloud Build packaging:

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  generativelanguage.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  logging.googleapis.com
```

---

### Phase 2: Containerization & Build Verification
Our container recipe is encapsulated in [`Dockerfile`](../Dockerfile) and optimized with [`.dockerignore`](../.dockerignore):
- **Base Image:** `python:3.12-slim`
- **Port:** `8080` (Cloud Run default)
- **Source Scope:** Bundles `src/thinking_partner/` and sample seed data.

---

### Phase 3: Automated One-Command Cloud Run Deployment
Deploy directly from local source code using Google Cloud Build (no local Docker daemon required):

```bash
gcloud run deploy collaborative-thinking-partner \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars USE_VERTEX_AI=true,GCP_PROJECT_ID=YOUR_PROJECT_ID,GCP_REGION=global,GEMINI_MODEL=gemini-3.7-flash,STORAGE_MODE=memory
```

*Flags explained:*
- `--source .`: Triggers Cloud Build to package the container in Artifact Registry.
- `--allow-unauthenticated`: Provides a public HTTPS URL for hackathon judges to interact with the live UI.
- `--set-env-vars`: Injects Vertex AI configuration into the runtime environment.

---

### Phase 4: Verification, Telemetry & Judging Proof
1. **Live Web Verification:** Open the provided `https://collaborative-thinking-partner-*.run.app` URL to verify split-pane dialogue and live ADR mutation.
2. **Cloud Trace / Logging Verification:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=collaborative-thinking-partner" --limit 20
   ```
3. **Demo Video Recording Blueprint (4-Minute Target):**
   - **Minute 0:00–0:45:** The Problem — LLMs default to generic advice; we debug problem structure with cognitive grammar.
   - **Minute 0:45–1:30:** Architecture Overview — 5-Phase State Machine, Problem Graph, and Gemini 3.7 Flash via Vertex AI.
   - **Minute 1:30–3:15:** Live Interactive Demo — Leadership worked example (Variant B deepening ladder descent and real-time ADR diff mutation).
   - **Minute 3:15–4:00:** GCP Proof & Cloud Run Dashboard — Showing Cloud Run metrics, Vertex AI API calls, and Cloud Logging traces.
