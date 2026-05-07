import json
from pathlib import Path
from typing import List, Optional
from src.models import Objection


class ObjectionBank:
    def __init__(self, filepath: str = "objections.json"):
        self.filepath = Path(filepath)
        self.objections: List[Objection] = self._load()

    def _load(self) -> List[Objection]:
        if not self.filepath.exists():
            return []

        with open(self.filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [Objection(**obj) for obj in data.get('objections', [])]

    def get_all(self) -> List[Objection]:
        """Return all objections"""
        return self.objections

    def get_by_id(self, obj_id: str) -> Optional[Objection]:
        """Get objection by ID"""
        for obj in self.objections:
            if obj.id == obj_id:
                return obj
        return None

    def get_by_category(self, category: str) -> List[Objection]:
        """Get all objections by category"""
        return [obj for obj in self.objections if obj.category == category]

    def get_by_difficulty(self, difficulty: int) -> List[Objection]:
        """Get all objections by difficulty level (1-3)"""
        return [obj for obj in self.objections if obj.dificuldade == difficulty]

    def get_by_multiple_categories(self, categories: List[str]) -> List[Objection]:
        """Get objections from multiple categories"""
        return [obj for obj in self.objections if obj.category in categories]

    def get_by_multiple_difficulties(self, difficulties: List[int]) -> List[Objection]:
        """Get objections with multiple difficulty levels"""
        return [obj for obj in self.objections if obj.dificuldade in difficulties]

    def search_by_keyword(self, keyword: str) -> List[Objection]:
        """Search objections by keyword in the objection text"""
        keyword_lower = keyword.lower()
        return [obj for obj in self.objections
                if keyword_lower in obj.objection.lower()]

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return list(set(obj.category for obj in self.objections))

    def get_difficulty_distribution(self) -> dict:
        """Get distribution of objections by difficulty"""
        distribution = {1: 0, 2: 0, 3: 0}
        for obj in self.objections:
            distribution[obj.dificuldade] += 1
        return distribution

    def get_category_distribution(self) -> dict:
        """Get distribution of objections by category"""
        distribution = {}
        for obj in self.objections:
            distribution[obj.category] = distribution.get(obj.category, 0) + 1
        return distribution

    def get_total_count(self) -> int:
        """Get total number of objections"""
        return len(self.objections)
