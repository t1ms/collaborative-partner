"""FastAPI Server exposing the Collaborative Thinking Partner REST API and Split-Pane Web UI."""

from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .agent.models import ProblemGraph, StatePhase
from .agent.orchestrator import ThinkingPartnerOrchestrator
from .graph.store import ProblemGraphStore
from .graph.taste_bank import TasteBank
from .tools.ingest_source import SourceIngestionTool

app = FastAPI(
    title="Collaborative Thinking Partner API",
    description="Deterministic Socratic Problem-Clarification Engine with Problem Graph & Live ADR Mutation",
    version="1.0.0",
)

store = ProblemGraphStore()
taste_bank = TasteBank()
orchestrator = ThinkingPartnerOrchestrator()
ingestion_tool = SourceIngestionTool()

WEB_DIR = Path(__file__).resolve().parent / "web"
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    user_id: str = "default_user"


class IngestRequest(BaseModel):
    session_id: Optional[str] = None
    source_name: str
    raw_text: str


@app.get("/")
def get_index():
    """Serves the split-pane UI."""
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Collaborative Thinking Partner API running. Web UI not found."}


@app.get("/healthz")
def healthz():
    """Health check endpoint for Cloud Run and local monitoring."""
    return {"status": "ok", "service": "collaborative-thinking-partner"}


@app.post("/api/session/new")
def new_session(user_id: str = "default_user"):
    """Creates a new session with loaded user taste profile."""
    profile = taste_bank.get_profile(user_id)
    graph = store.get_or_create()
    graph.taste_profile = profile
    store.save(graph)
    return {
        "session_id": graph.session_id,
        "phase": graph.current_phase,
        "taste_profile": graph.taste_profile,
    }


@app.get("/api/session/{session_id}")
def get_session(session_id: str):
    """Retrieves current session state, graph, and latest ADR artifact."""
    graph = store.load(session_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Session not found")
    latest_art = graph.artifacts[-1] if graph.artifacts else None
    return {
        "graph": graph,
        "latest_artifact": latest_art,
    }


@app.post("/api/chat")
def chat(req: ChatRequest):
    """Executes a Socratic turn."""
    graph = store.get_or_create(req.session_id)

    response_text, updated_graph, updated_artifact = orchestrator.process_turn(
        graph, req.message
    )

    # If completed S6, record self-improvement in taste bank
    if updated_graph.current_phase == StatePhase.S6_DONE:
        resolved_count = len([d for d in updated_graph.detections if d.resolved])
        deepen_count = sum(d.deepen_count for d in updated_graph.detections)
        taste_bank.record_session_completion(req.user_id, resolved_count, deepen_count)

    store.save(updated_graph)

    return {
        "session_id": updated_graph.session_id,
        "response": response_text,
        "current_phase": updated_graph.current_phase,
        "active_detection_id": updated_graph.active_detection_id,
        "graph": updated_graph,
        "latest_artifact": updated_artifact,
    }


@app.post("/api/ingest")
def ingest(req: IngestRequest):
    """Ingests unstructured source text."""
    graph = store.get_or_create(req.session_id)
    node = ingestion_tool.ingest_text_source(graph, req.source_name, req.raw_text)
    store.save(graph)
    return {
        "session_id": graph.session_id,
        "ingested_node": node,
    }


@app.get("/api/taste/{user_id}")
def get_taste(user_id: str):
    """Fetches user taste profile."""
    return taste_bank.get_profile(user_id)


@app.get("/api/demo-scenarios")
def get_demo_scenarios():
    """Returns curated demo scenarios for testing and demonstration."""
    return [
        {
            "id": "leadership_material",
            "title": "Leadership Validation (Mind Reading & Deepening)",
            "initial_prompt": "They don't think I'm leadership material because I'm not loud in executive meetings.",
            "description": "Tests Mind-Reading detection, bedrock descent, and 2-cycle deepening ladder on fast closure.",
        },
        {
            "id": "dual_horizon_burnout",
            "title": "Dual-Horizon Burnout (Upstream Exhaustion + Downstream Friction)",
            "initial_prompt": "I'm completely exhausted and barely getting by, and I hate that I spend evenings scrolling on my phone instead of with my family.",
            "description": "Tests Dual-Horizon Triage: Upstream state linked to Downstream acute symptom with micro-container relief.",
        },
        {
            "id": "cofounder_conflict",
            "title": "Co-founder Priority Conflict (Universal Quantifier & Modals)",
            "initial_prompt": "My co-founder always ignores our roadmap and we must pivot every single week or we'll run out of runway.",
            "description": "Tests Universal Quantifiers, Modal Necessity, and Well-Formed Outcome architecture.",
        },
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
