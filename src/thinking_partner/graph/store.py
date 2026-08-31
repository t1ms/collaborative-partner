import json
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Optional
from ..agent.models import ProblemGraph
from ..agent.classifier import is_crisis_imminent, is_crisis_distress
from ..config import DATA_DIR, STORAGE_MODE, GCP_PROJECT_ID

MAX_ACTIVE_SESSIONS = 1000


class ProblemGraphStore:
    """Persistent storage for Problem Graphs across turns and sessions with LRU cache bounds."""

    def __init__(self, storage_dir: Optional[Path] = None, max_sessions: int = MAX_ACTIVE_SESSIONS):
        self.storage_dir = storage_dir or (DATA_DIR / "sessions")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.max_sessions = max_sessions
        self._memory_cache: OrderedDict[str, ProblemGraph] = OrderedDict()

    def save(self, graph: ProblemGraph) -> None:
        """Persists the ProblemGraph to memory and JSON checkpoint with LRU bounds and crisis redaction."""
        if graph.session_id in self._memory_cache:
            self._memory_cache.move_to_end(graph.session_id)
        self._memory_cache[graph.session_id] = graph

        # Evict oldest in-memory session if capacity exceeded
        if len(self._memory_cache) > self.max_sessions:
            self._memory_cache.popitem(last=False)

        # Redact raw self-harm / crisis statements in disk persistence
        data = graph.model_dump(mode="json")
        for u in data.get("utterances", []):
            text = u.get("text", "")
            if is_crisis_imminent(text) or is_crisis_distress(text):
                u["text"] = "[Crisis Support Offered - Utterance Redacted for Safety & Privacy]"

        file_path = self.storage_dir / f"{graph.session_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, session_id: str) -> Optional[ProblemGraph]:
        """Loads a ProblemGraph by session ID."""
        if session_id in self._memory_cache:
            self._memory_cache.move_to_end(session_id)
            return self._memory_cache[session_id]

        file_path = self.storage_dir / f"{session_id}.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                graph = ProblemGraph.model_validate(data)
                self._memory_cache[session_id] = graph
                if len(self._memory_cache) > self.max_sessions:
                    self._memory_cache.popitem(last=False)
                return graph
        return None

    def get_or_create(self, session_id: Optional[str] = None) -> ProblemGraph:
        """Returns existing graph or initializes a new one."""
        if session_id:
            existing = self.load(session_id)
            if existing:
                return existing
        new_graph = ProblemGraph()
        self.save(new_graph)
        return new_graph

