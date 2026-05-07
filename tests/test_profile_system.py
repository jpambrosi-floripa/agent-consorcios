import pytest
from src.profile_system import ProfileSystem

def test_load_all_profiles():
    system = ProfileSystem("profiles")
    profiles = system.get_all()
    assert len(profiles) >= 3
    names = [p.name for p in profiles]
    assert "Investidor Analítico" in names

def test_get_profile_by_name():
    system = ProfileSystem("profiles")
    prof = system.get_by_name("investment-focused")
    assert prof is not None
    assert prof.personality is not None

def test_get_objection_priority():
    system = ProfileSystem("profiles")
    prof = system.get_by_name("investment-focused")
    priority = prof.objection_priority
    assert isinstance(priority, list)
    assert len(priority) > 0

def test_nonexistent_profile_returns_none():
    system = ProfileSystem("profiles")
    prof = system.get_by_name("nonexistent")
    assert prof is None
