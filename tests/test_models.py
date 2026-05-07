import pytest
from datetime import datetime
from src.models import (
    Message, Objection, ObjectionUsage, Session, Profile
)

def test_message_creation():
    msg = Message(role="user", content="Hello", timestamp=datetime.now())
    assert msg.role == "user"
    assert msg.content == "Hello"

def test_objection_creation():
    obj = Objection(
        id="taxa_admin",
        category="financial",
        objection="What's the fee?",
        variações=["How much?"],
        técnicas_esperadas=["explain"],
        dificuldade=2
    )
    assert obj.id == "taxa_admin"
    assert obj.category == "financial"

def test_objection_usage():
    usage = ObjectionUsage(id="taxa_admin", order=1, status="contornada")
    assert usage.status == "contornada"

def test_session_creation():
    msg = Message(role="user", content="Hi", timestamp=datetime.now())
    session = Session(
        id="session-001",
        profile="investment-focused",
        messages=[msg],
        objections_used=[]
    )
    assert session.id == "session-001"
    assert len(session.messages) == 1

def test_profile_creation():
    profile = Profile(
        name="Test",
        personality="test",
        objectives=["obj1"],
        objection_priority=["obj1"],
        triggers={}
    )
    assert profile.name == "Test"
