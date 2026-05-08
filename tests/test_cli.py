import pytest
from typer.testing import CliRunner
from src.session_manager import SessionManager
from src.profile_system import ProfileSystem

runner = CliRunner()


def test_session_manager_create():
    """Test SessionManager creates sessions correctly"""
    mgr = SessionManager(sessions_dir="sessions")
    session = mgr.create_session(profile="test_profile")
    assert session.id is not None
    assert session.profile == "test_profile"
    assert len(session.messages) == 0


def test_session_manager_save_load():
    """Test SessionManager saves and loads sessions"""
    mgr = SessionManager(sessions_dir="sessions")
    session = mgr.create_session(profile="test_profile")
    session_id = session.id

    loaded = mgr.load_session(session_id)
    assert loaded is not None
    assert loaded.id == session_id
    assert loaded.profile == "test_profile"


def test_session_manager_list():
    """Test SessionManager lists sessions"""
    mgr = SessionManager(sessions_dir="sessions")
    sessions = mgr.list_sessions()
    assert isinstance(sessions, list)


def test_session_manager_delete():
    """Test SessionManager deletes sessions"""
    mgr = SessionManager(sessions_dir="sessions")
    session = mgr.create_session(profile="test_profile")
    session_id = session.id

    mgr.delete_session(session_id)
    loaded = mgr.load_session(session_id)
    assert loaded is None


def test_profile_system_load():
    """Test ProfileSystem loads profiles"""
    profile_sys = ProfileSystem(profiles_dir="profiles")
    profiles = profile_sys.get_all()
    # Should have at least the profiles defined in the project
    assert isinstance(profiles, list)


def test_profile_system_get_by_name():
    """Test ProfileSystem retrieves profiles by name"""
    profile_sys = ProfileSystem(profiles_dir="profiles")
    available = profile_sys.list_available()
    if available:
        profile_name = available[0]
        profile = profile_sys.get_by_name(profile_name)
        assert profile is not None
        assert profile.name == profile_name
