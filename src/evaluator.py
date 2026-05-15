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

    TECHNIQUE_HINTS = {
        "explicar_competitividade": "Cite uma taxa específica e compare com concorrentes: 'nossa taxa média é X%, abaixo da média do mercado de Y%'.",
        "comparar_com_alternativas": "Mostre a desvantagem da alternativa que o cliente mencionou — juros do financiamento, inflação da poupança, risco de ações.",
        "reframing": "Reframe o custo como investimento: a taxa paga o grupo gestor que garante a carta de crédito.",
        "seguranca_bacen": "Mencione que consórcios são regulados pelo Banco Central — isso diferencia de pirâmide ou investimento informal.",
        "explicar_funcionamento": "Explique o mecanismo em 1 frase simples: 'todo mês o grupo se reúne, arrecada as parcelas e sorteiam quem recebe a carta de crédito'.",
        "mostrar_lance": "Destaque que além do sorteio o cliente pode dar um lance e antecipar a contemplação.",
        "comparar_financiamento": "Compare diretamente: financiamento tem juros de 10-15% ao ano, consórcio tem taxa administrativa de 1-2% ao ano sobre o total.",
        "comparar_poupança": "Poupança rende menos que a inflação e exige disciplina — consórcio é disciplina automática com poder de compra garantido.",
        "prazo_flexivel": "Mencione que o prazo pode ser encurtado com lances e que a carta pode ser usada a qualquer momento após contemplação.",
        "garantia_contemplacao": "Esclareça que todos são contemplados antes do fim do plano — sorteio ou lance.",
    }

    def _build_hint(self, overcome: bool, techniques_used: List[str], objection: Objection) -> str:
        expected = objection.técnicas_esperadas
        if overcome:
            used_expected = [t for t in techniques_used if t in expected or t in self.TECHNIQUE_HINTS]
            if used_expected:
                first = used_expected[0]
                label = first.replace("_", " ").capitalize()
                return f"Boa abordagem com '{label}'. Para reforçar ainda mais: {self.TECHNIQUE_HINTS.get(first, 'continue nessa linha nas próximas objeções.')}".rstrip(".")  + "."
            return "Boa resposta! Continue mantendo comparações concretas e linguagem direta."
        else:
            missing = [t for t in expected if t not in techniques_used]
            hints = [self.TECHNIQUE_HINTS[t] for t in missing if t in self.TECHNIQUE_HINTS]
            if hints:
                return "Tente: " + " / ".join(hints[:2])
            return f"Aborde diretamente a preocupação do cliente sobre '{objection.objection.lower()}'."

    def evaluate_response(
        self,
        vendor_response: str,
        objection: Objection,
        conversation_history=None,
        agent=None,
    ) -> Dict:
        response_lower = vendor_response.lower()

        if any(word in response_lower for word in self.EVASION_KEYWORDS):
            hint = self._get_hint(False, [], objection, vendor_response, conversation_history, agent)
            return {
                "overcome": False,
                "reason": "vendor_evaded",
                "techniques": [],
                "hint": hint,
            }

        objection_id = objection.id
        keywords = self.OVERCOME_KEYWORDS.get(objection_id, [])
        found_keywords = sum(1 for kw in keywords if kw in response_lower)

        overcome = found_keywords >= 1
        techniques = self.detect_techniques(vendor_response)
        hint = self._get_hint(overcome, techniques, objection, vendor_response, conversation_history, agent)

        return {
            "overcome": overcome,
            "reason": "addressed" if overcome else "not_addressed",
            "techniques": techniques,
            "hint": hint,
        }

    def _get_hint(self, overcome: bool, techniques: list, objection: Objection, vendor_response: str, conversation_history, agent) -> str:
        if agent and conversation_history is not None:
            try:
                llm_hint = agent.evaluate_vendor_response(vendor_response, objection, conversation_history)
                if llm_hint:
                    return llm_hint
            except Exception:
                pass
        return self._build_hint(overcome, techniques, objection)

    def detect_techniques(self, response: str) -> List[str]:
        response_lower = response.lower()
        found = []

        for technique, pattern in self.TECHNIQUE_PATTERNS.items():
            if re.search(pattern, response_lower):
                found.append(technique)

        return found
