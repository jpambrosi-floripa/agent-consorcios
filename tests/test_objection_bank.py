import pytest
from src.objection_bank import ObjectionBank
from src.models import Objection


def test_load_objections():
    bank = ObjectionBank("objections.json")
    objections = bank.get_all()
    assert len(objections) > 0
    assert all(isinstance(o, Objection) for o in objections)


def test_get_objection_by_id():
    bank = ObjectionBank("objections.json")
    obj = bank.get_by_id("taxa_administrativa")
    assert obj is not None
    assert obj.id == "taxa_administrativa"


def test_get_objection_by_category():
    bank = ObjectionBank("objections.json")
    financial = bank.get_by_category("financial")
    assert len(financial) > 0
    assert all(o.category == "financial" for o in financial)


def test_nonexistent_objection_returns_none():
    bank = ObjectionBank("objections.json")
    obj = bank.get_by_id("nonexistent")
    assert obj is None


def test_total_objections_50():
    bank = ObjectionBank("objections.json")
    objections = bank.get_all()
    assert len(objections) == 50


def test_objection_structure():
    bank = ObjectionBank("objections.json")
    obj = bank.get_all()[0]
    assert hasattr(obj, 'id')
    assert hasattr(obj, 'category')
    assert hasattr(obj, 'objection')
    assert hasattr(obj, 'variações')
    assert hasattr(obj, 'técnicas_esperadas')
    assert hasattr(obj, 'dificuldade')


def test_get_by_difficulty():
    bank = ObjectionBank("objections.json")
    easy = bank.get_by_difficulty(1)
    medium = bank.get_by_difficulty(2)
    hard = bank.get_by_difficulty(3)
    assert all(o.dificuldade == 1 for o in easy)
    assert all(o.dificuldade == 2 for o in medium)
    assert all(o.dificuldade == 3 for o in hard)


def test_all_categories_present():
    bank = ObjectionBank("objections.json")
    categories = set(o.category for o in bank.get_all())
    expected_categories = {
        'financial', 'operational', 'behavioral', 'comparative',
        'market_timing', 'property_requirements', 'cash_flow',
        'psychological', 'lifestyle', 'family_concerns'
    }
    assert len(categories) >= 5
