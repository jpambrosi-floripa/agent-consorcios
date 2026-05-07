import pytest
from src.evaluator import Evaluator
from src.models import Objection

def test_detect_objection_overcome_positive():
    evaluator = Evaluator()
    objection = Objection(
        id="taxa",
        category="financial",
        objection="Taxa é alta",
        variações=[],
        técnicas_esperadas=["explicar_competitividade"],
        dificuldade=2
    )

    vendor_response = "A taxa é 2% e isso é bem competitivo comparado com outras instituições"
    result = evaluator.evaluate_response(vendor_response, objection)
    assert result["overcome"] == True

def test_detect_objection_not_overcome():
    evaluator = Evaluator()
    objection = Objection(
        id="taxa",
        category="financial",
        objection="Taxa é alta",
        variações=[],
        técnicas_esperadas=["explicar_competitividade"],
        dificuldade=2
    )

    vendor_response = "Boa pergunta, vou voltar nesse ponto depois"
    result = evaluator.evaluate_response(vendor_response, objection)
    assert result["overcome"] == False

def test_detect_technique():
    evaluator = Evaluator()
    response = "Comparando com o financiamento tradicional..."
    techniques = evaluator.detect_techniques(response)
    assert len(techniques) > 0
