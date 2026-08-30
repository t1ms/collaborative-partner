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
OVERLAY_DIR = Path(__file__).resolve().parent.parent.parent / "02_map" / "overlays"

