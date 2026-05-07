import re
from typing import Dict, List, Optional
from src.models import Objection

class Evaluator:
    # Keywords that indicate addressing an objection
    OVERCOME_KEYWORDS = {
        "taxa": ["competitivo", "comparado", "mercado", "justifica", "explicar"],
        "rentabilidade": ["retorno", "comparar", "mercado", "alternativa", "ganho"],
        "liquidez": ["sacar", "resgate", "antes", "antecipada", "resgata"],
        "prazo": ["tempo", "quanto tempo", "longo", "comparar", "financiamento"],
        "sorteio": ["chance", "probabilidade", "segura", "garantia", "todas"],
        "entrada": ["parcelado", "entrada menor", "opção", "flexibilidade"],
        "financiamento": ["diferença", "juros", "taxa", "seguro", "diferente"],
        "poupança": ["rentabilidade", "disciplina", "tempo", "ganho", "comparar"],
    }

    EVASION_KEYWORDS = [
        "voltar depois",
        "nesse ponto",
        "depois a gente",
        "deixa eu",
        "você quer saber",
        "ótima pergunta"
    ]

    TECHNIQUE_PATTERNS = {
        "explicacao_comparativa": r"comparad|comparar|compar",
        "reframing": r"diferente|diferença|não é|na verdade",
        "questionamento_controladoria": r"você acha|qual seria|como você",
        "seguranca": r"seguro|garantid|regulad|fundo",
        "alternativa_oferta": r"outra opção|alternative|outro produto",
    }

    def evaluate_response(self, vendor_response: str, objection: Objection) -> Dict:
        response_lower = vendor_response.lower()

        # Check if response avoids the question
        if any(word in response_lower for word in self.EVASION_KEYWORDS):
            return {
                "overcome": False,
                "reason": "vendor_evaded",
                "techniques": []
            }

        # Check if response addresses objection keywords
        objection_id = objection.id
        keywords = self.OVERCOME_KEYWORDS.get(objection_id, [])

        found_keywords = sum(
            1 for keyword in keywords
            if keyword in response_lower
        )

        overcome = found_keywords >= 1
        techniques = self.detect_techniques(vendor_response)

        return {
            "overcome": overcome,
            "reason": "addressed" if overcome else "not_addressed",
            "techniques": techniques
        }

    def detect_techniques(self, response: str) -> List[str]:
        response_lower = response.lower()
        found = []

        for technique, pattern in self.TECHNIQUE_PATTERNS.items():
            if re.search(pattern, response_lower):
                found.append(technique)

        return found
