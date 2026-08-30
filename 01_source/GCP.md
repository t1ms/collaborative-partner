# GCP Architecture & Deployment Guidance for Agents

> **Context for Agents:** This repository runs on **Google Cloud Platform (GCP)** leveraging **Vertex AI (Gemini 3.7 Flash)**, **Cloud Run v2**, **Artifact Registry**, **Firestore**, and **Cloud Logging**.
> Use this document as the master index for navigating GCP architecture, infrastructure-as-code (Terraform), pre-flight checks, and deployment runbooks.

---

## 🧭 Which GCP Guide to Consult

The parent workspace contains two authoritative guides. Follow this routing table based on the task:

| Agent Task | Consult Document | Description |
|---|---|---|
| **Infrastructure Design, Terraform Blueprints & Service Sizing** | [**`../GCP Architectural Knowledge.md`**](../../GCP%20Architectural%20Knowledge.md) | **The 10-Module Encyclopedia:** Production Terraform for Shared VPC, Cloud Armor, Cloud Run v2 (Direct VPC Egress), GKE Autopilot, Spanner/AlloyDB/Bigtable, BigQuery, Vertex AI Model Garden/Feature Store, Cloud KMS/HSM, Workload Identity Federation (WIF), Cloud Monitoring/Logging, and FinOps automation. |
| **CLI Runbook, Pre-Flight Verification & Conventions** | [**`../GCP_GUIDE.md`**](../../GCP_GUIDE.md) | **The Operational Runbook:** Normative `gcloud` conventions (`--project` + `--format=json`), session pre-flight checks (§2), least-privilege IAM rules (§4), safe execution guardrails (§7), troubleshooting matrix (§10), and copy-paste CLI recipes. |
| **Collaborative Partner Cloud Run Deployment** | [**`03_agent-system/gcp-deployment-plan.md`**](../03_agent-system/gcp-deployment-plan.md) | **Project-Specific Plan:** Cloud Run container build, environment variable injection, Vertex AI ADC wiring, structured logging traces, and hackathon judging demo proof. |

---

## ⚡ Normative Rules for AI Agents Working with GCP

1. **Pre-Flight First:** Always run §2 pre-flight checks from [`../../GCP_GUIDE.md`](../../GCP_GUIDE.md) before proposing or running mutations:
   ```bash
   gcloud config list --format=json
   gcloud projects describe <PROJECT_ID> --format=json
   gcloud billing projects describe <PROJECT_ID> --format=json
   ```
2. **Explicit Project Scoping:** Never rely on ambient gcloud state. Always append `--project=<PROJECT_ID>` and `--format=json` to read queries.
3. **Least-Privilege Workload SAs:** Never assign `roles/owner` or `roles/editor` to workload service accounts. Use `roles/aiplatform.user` for Vertex AI and `roles/logging.logWriter` for Cloud Logging.
4. **No Hardcoded Keys:** In Cloud Run, rely on the runtime attached Service Account metadata server (`vertexai=True` in `google-genai` SDK). For CI/CD, use Workload Identity Federation (WIF).
5. **Impact Plan for Destructive Actions:** Output target, blast radius, data loss risk, and rollback procedure before modifying disks, clusters, or deleting resources.

---

## 🚀 Quick Deployment Recipe for `collaborative-partner`

### 1. Enable Services
```bash
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  --project=<PROJECT_ID>
```

### 2. Configure Runtime Service Account
```bash
gcloud iam service-accounts create sa-thinking-partner \
  --display-name="Collaborative Thinking Partner Runtime SA" \
  --project=<PROJECT_ID>

gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member="serviceAccount:sa-thinking-partner@<PROJECT_ID>.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member="serviceAccount:sa-thinking-partner@<PROJECT_ID>.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"
```

### 3. Build & Deploy to Cloud Run
```bash
# Direct source deploy via Cloud Build
gcloud run deploy collaborative-thinking-partner \
  --source . \
  --region us-central1 \
  --project=<PROJECT_ID> \
  --service-account=sa-thinking-partner@<PROJECT_ID>.iam.gserviceaccount.com \
  --set-env-vars="USE_VERTEX_AI=true,GCP_PROJECT_ID=<PROJECT_ID>,GCP_REGION=us-central1,GEMINI_MODEL=gemini-3.7-flash,STORAGE_MODE=memory" \
  --allow-unauthenticated \
  --port=8080 \
  --format=json
```

---

## 🔗 Key Code & Configuration References

* [Dockerfile](../Dockerfile) — Cloud Run container specification.
* [.env.example](../.env.example) — Local dev & Vertex AI environment configuration.
* [orchestrator.py](../src/thinking_partner/agent/orchestrator.py) — `google-genai` SDK Vertex AI client initialization.
* [server.py](../src/thinking_partner/server.py) — FastAPI web and SSE endpoint handlers.
