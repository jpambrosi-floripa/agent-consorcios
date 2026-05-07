import pytest
import random
from src.objection_selector import ObjectionSelector
from src.objection_bank import ObjectionBank
from src.profile_system import ProfileSystem
from src.models import Session, ObjectionUsage
from datetime import datetime


@pytest.fixture
def selector():
    bank = ObjectionBank("objections.json")
    system = ProfileSystem("profiles")
    return ObjectionSelector(bank, system)


def test_select_first_objection(selector):
    """Test that first selection follows profile priority order"""
    random.seed(0)  # Seed for deterministic behavior (ensures >= 0.2)
    session = Session(id="test", profile="investment-focused", messages=[])
    objection = selector.select_next(session)
    assert objection is not None
    assert objection.id == "taxa_administrativa"


def test_select_next_respects_priority(selector):
    """Test that second selection follows priority after first is used"""
    random.seed(0)  # Seed for deterministic behavior (sequential picks)
    session = Session(id="test", profile="investment-focused", messages=[])
    obj1 = selector.select_next(session)
    assert obj1.id == "taxa_administrativa"

    # After first, should be second in priority
    session.objections_used.append(
        ObjectionUsage(id="taxa_administrativa", order=1, status="contornada")
    )
    obj2 = selector.select_next(session)
    assert obj2.id == "rentabilidade_baixa"


def test_select_skips_used_objections(selector):
    """Test that used objections are skipped"""
    random.seed(0)  # Seed for deterministic behavior
    session = Session(id="test", profile="investment-focused", messages=[])
    session.objections_used = [
        ObjectionUsage(id="taxa_administrativa", order=1, status="contornada"),
        ObjectionUsage(id="rentabilidade_baixa", order=2, status="não_contornada"),
    ]
    obj = selector.select_next(session)
    assert obj.id == "liquidez_baixa"


def test_select_stops_at_10_objections(selector):
    """Test that no more objections are selected after max of 10"""
    random.seed(0)  # Seed for deterministic behavior
    session = Session(id="test", profile="investment-focused", messages=[])
    for i in range(10):
        session.objections_used.append(
            ObjectionUsage(id=f"obj_{i}", order=i, status="contornada")
        )
    obj = selector.select_next(session)
    assert obj is None  # No more objections
