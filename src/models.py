from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional

class Message(BaseModel):
    role: str  # "user" or "agent"
    content: str
    timestamp: datetime
    objection_id: Optional[str] = None

class Objection(BaseModel):
    id: str
    category: str
    objection: str
    variações: List[str]
    técnicas_esperadas: List[str]
    dificuldade: int

class ObjectionUsage(BaseModel):
    id: str
    order: int
    status: str  # "contornada" or "não_contornada"

class Session(BaseModel):
    id: str
    profile: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    messages: List[Message] = []
    objections_used: List[ObjectionUsage] = []

    @property
    def duration_minutes(self) -> int:
        if not self.messages:
            return 0
        start = self.messages[0].timestamp
        end = self.messages[-1].timestamp
        return int((end - start).total_seconds() / 60)

class Profile(BaseModel):
    name: str
    personality: str
    objectives: List[str]
    objection_priority: List[str]
    triggers: Dict[str, str] = {}

class Report(BaseModel):
    session_id: str
    profile: str
    duration: int
    total_objections: int
    overcome: int
    not_overcome: int
    score: float
    techniques: List[str]
    recommendations: List[str]
    objection_analyses: List[Dict] = []
    behavioral_patterns: Dict = {}
    priority_improvements: List[str] = []
    spin_recommendations: List[Dict] = []
