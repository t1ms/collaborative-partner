"""Problem Graph persistence engine with Firestore and local JSON checkpointing."""

import json
from pathlib import Path
from typing import Dict, Optional
from ..agent.models import ProblemGraph
from ..config import DATA_DIR, STORAGE_MODE, GCP_PROJECT_ID


class ProblemGraphStore:
    """Persistent storage for Problem Graphs across turns and sessions."""

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or (DATA_DIR / "sessions")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, ProblemGraph] = {}

    def save(self, graph: ProblemGraph) -> None:
        """Persists the ProblemGraph to memory and JSON checkpoint."""
        self._memory_cache[graph.session_id] = graph

        file_path = self.storage_dir / f"{graph.session_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(graph.model_dump_json(indent=2))

    def load(self, session_id: str) -> Optional[ProblemGraph]:
        """Loads a ProblemGraph by session ID."""
        if session_id in self._memory_cache:
            return self._memory_cache[session_id]

        file_path = self.storage_dir / f"{session_id}.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                graph = ProblemGraph.model_validate(data)
                self._memory_cache[session_id] = graph
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
