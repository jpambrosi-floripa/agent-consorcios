import json
from pathlib import Path
from typing import List, Optional
from src.models import Profile

class ProfileSystem:
    def __init__(self, profiles_dir: str = "profiles"):
        self.profiles_dir = Path(profiles_dir)
        self.profiles: List[Profile] = self._load_all()

    def _load_all(self) -> List[Profile]:
        profiles = []
        for filepath in self.profiles_dir.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            profiles.append(Profile(**data))
        return profiles

    def get_all(self) -> List[Profile]:
        return self.profiles

    def get_by_name(self, profile_name: str) -> Optional[Profile]:
        # Try matching by profile display name first
        for prof in self.profiles:
            if prof.name.lower() == profile_name.lower():
                return prof

        # Try matching by filename (without .json)
        filename_without_ext = profile_name.lower()
        for filepath in self.profiles_dir.glob("*.json"):
            if filepath.stem.lower() == filename_without_ext:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return Profile(**data)

        return None

    def list_available(self) -> List[str]:
        return [p.name for p in self.profiles]
