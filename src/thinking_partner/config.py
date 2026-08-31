"""Configuration management for Collaborative Thinking Partner."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load local .env if present
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
GCP_REGION = os.getenv("GCP_REGION", "us-central1")
USE_VERTEX_AI = os.getenv("USE_VERTEX_AI", "false").lower() in ("true", "1", "yes")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "false").lower() in ("true", "1", "yes")

# Persistence mode: 'firestore' or 'memory' (with automatic JSON file checkpointing)
STORAGE_MODE = os.getenv("STORAGE_MODE", "memory")
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Domain Switch & Fluidity Dials
DOMAIN_SWITCH_THRESHOLD = float(os.getenv("DOMAIN_SWITCH_THRESHOLD", "0.60"))
DOMAIN_MARGIN = float(os.getenv("DOMAIN_MARGIN", "0.15"))
DOMAIN_HYSTERESIS = int(os.getenv("DOMAIN_HYSTERESIS", "2"))
DOMAIN_BLEND = os.getenv("DOMAIN_BLEND", "true").lower() in ("true", "1", "yes")
DOMAIN_LLM_ENABLED = os.getenv("DOMAIN_LLM_ENABLED", "true").lower() in ("true", "1", "yes")
DOMAIN_LLM_WEIGHT = float(os.getenv("DOMAIN_LLM_WEIGHT", "1.5"))
DOMAIN_LLM_TIMEOUT_MS = int(os.getenv("DOMAIN_LLM_TIMEOUT_MS", "2000"))
OVERLAY_DIR = Path(__file__).resolve().parent.parent.parent / "02_map" / "overlays"

# Socratic Deepening & Ecology Caps per Domain
DOMAIN_MAX_DEEPEN = {
    "se": int(os.getenv("DOMAIN_MAX_DEEPEN_SE", "1")),
    "design": int(os.getenv("DOMAIN_MAX_DEEPEN_DESIGN", "1")),
    "leadership": int(os.getenv("DOMAIN_MAX_DEEPEN_LEADERSHIP", "2")),
    "general": int(os.getenv("DOMAIN_MAX_DEEPEN_GENERAL", "2")),
}
DOMAIN_ECOLOGY_CAPS = {
    "se": int(os.getenv("DOMAIN_ECOLOGY_CAPS_SE", "1")),
    "design": int(os.getenv("DOMAIN_ECOLOGY_CAPS_DESIGN", "1")),
    "leadership": int(os.getenv("DOMAIN_ECOLOGY_CAPS_LEADERSHIP", "2")),
    "general": int(os.getenv("DOMAIN_ECOLOGY_CAPS_GENERAL", "1")),
}

# Session Capacity & Rate Limiting Dials
TURN_MAX_OUTPUT_TOKENS = int(os.getenv("TURN_MAX_OUTPUT_TOKENS", "1024"))
SESSION_MAX_TURNS = int(os.getenv("SESSION_MAX_TURNS", "40"))
SESSION_MAX_OUTPUT_TOKENS = int(os.getenv("SESSION_MAX_OUTPUT_TOKENS", "40000"))
RATE_LIMIT_TURNS_PER_MIN = int(os.getenv("RATE_LIMIT_TURNS_PER_MIN", "10"))

# Crisis & Urgency Triage Dials
CRISIS_ENABLED = os.getenv("CRISIS_ENABLED", "true").lower() in ("true", "1", "yes")
URGENCY_ENABLED = os.getenv("URGENCY_ENABLED", "true").lower() in ("true", "1", "yes")



