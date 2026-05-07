import pytest
import json
import os
from datetime import datetime
from pathlib import Path
from src.session_manager import SessionManager
from src.models import Session, Message

@pytest.fixture
def session_manager(tmp_path):
    return SessionManager(sessions_dir=tmp_path)

def test_create_new_session(session_manager):
    session = session_manager.create_session("investment-focused")
    assert session.id.startswith("session-")
    assert session.profile == "investment-focused"
    assert session.messages == []

def test_load_session(session_manager):
    created = session_manager.create_session("investment-focused")
    loaded = session_manager.load_session(created.id)
    assert loaded.id == created.id
    assert loaded.profile == "investment-focused"

def test_save_message_to_session(session_manager):
    session = session_manager.create_session("investment-focused")
    msg = Message(role="user", content="Hi", timestamp=datetime.now())
    session.messages.append(msg)
    session_manager.save_session(session)

    loaded = session_manager.load_session(session.id)
    assert len(loaded.messages) == 1
    assert loaded.messages[0].content == "Hi"

def test_list_sessions(session_manager):
    session_manager.create_session("investment-focused")
    session_manager.create_session("home-buyer")

    sessions = session_manager.list_sessions()
    assert len(sessions) == 2

def test_delete_session(session_manager):
    session = session_manager.create_session("investment-focused")
    session_manager.delete_session(session.id)

    sessions = session_manager.list_sessions()
    assert len(sessions) == 0

def test_session_persistence(session_manager):
    session = session_manager.create_session("investment-focused")
    msg = Message(role="agent", content="Test", timestamp=datetime.now())
    session.messages.append(msg)
    session_manager.save_session(session)

    # Load from disk
    loaded = session_manager.load_session(session.id)
    assert loaded.messages[0].content == "Test"
