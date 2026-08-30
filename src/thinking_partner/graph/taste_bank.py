"""Taste Profile and Precedent Bank for cross-session self-improvement."""

import json
from pathlib import Path
from typing import Optional, Dict
from ..agent.models import TasteProfile
from ..config import DATA_DIR


class TasteBank:
    """Manages cross-session adaptation and user taste profiles."""

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or (DATA_DIR / "tastes")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, TasteProfile] = {}

    def get_profile(self, user_id: str = "default_user") -> TasteProfile:
        """Retrieves or initializes a user's taste profile."""
        if user_id in self._cache:
            return self._cache[user_id]

        file_path = self.storage_dir / f"{user_id}.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                profile = TasteProfile.model_validate(data)
                self._cache[user_id] = profile
                return profile

        profile = TasteProfile(user_id=user_id)
        self.save_profile(profile)
        return profile

    def save_profile(self, profile: TasteProfile) -> None:
        """Saves an updated profile."""
        self._cache[profile.user_id] = profile
        file_path = self.storage_dir / f"{profile.user_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(profile.model_dump_json(indent=2))

    def record_session_completion(self, user_id: str, resolved_count: int, deepen_count: int) -> TasteProfile:
        """Autonomous self-improvement: adapts depth and framing preference based on session trajectory."""
        profile = self.get_profile(user_id)
        profile.sessions_completed += 1

        # If user engages in deep descents (>2 deepening cycles), tune depth to first principles
        if deepen_count >= 2:
            profile.depth_preference = "first_principles"
            profile.framing_anchor = "bedrock"
        elif deepen_count == 0 and resolved_count <= 2:
            profile.depth_preference = "balanced"

        self.save_profile(profile)
        return profile
