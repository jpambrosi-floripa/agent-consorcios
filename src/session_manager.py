import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import uuid
from src.models import Session, Message

class SessionManager:
    def __init__(self, sessions_dir: str = "sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)

    def create_session(self, profile: str) -> Session:
        session_id = f"session-{str(uuid.uuid4())[:8]}"
        session = Session(id=session_id, profile=profile)
        self.save_session(session)
        return session

    def load_session(self, session_id: str) -> Optional[Session]:
        path = self.sessions_dir / f"{session_id}.json"
        if not path.exists():
            return None

        with open(path, 'r') as f:
            data = json.load(f)

        # Parse timestamps
        for msg in data.get('messages', []):
            msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])

        return Session(**data)

    def save_session(self, session: Session) -> None:
        session.updated_at = datetime.now()
        path = self.sessions_dir / f"{session.id}.json"

        # Convert to dict with ISO timestamp strings
        data = session.model_dump()
        data['created_at'] = session.created_at.isoformat()
        data['updated_at'] = session.updated_at.isoformat()
        for msg in data['messages']:
            msg['timestamp'] = msg['timestamp'].isoformat()

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def list_sessions(self) -> List[Session]:
        sessions = []
        for file in self.sessions_dir.glob("session-*.json"):
            session_id = file.stem
            session = self.load_session(session_id)
            if session:
                sessions.append(session)
        return sorted(sessions, key=lambda s: s.updated_at, reverse=True)

    def delete_session(self, session_id: str) -> None:
        path = self.sessions_dir / f"{session_id}.json"
        if path.exists():
            path.unlink()
