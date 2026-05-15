import json
from typing import List, Dict, Optional
from src.models import Profile, Objection, Message
import anthropic


class ClaudeAgent:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-haiku-4-5-20251001"
        self.report_model = "claude-sonnet-4-6"

    def _build_system_prompt(self, profile: Profile) -> str:
        return f"""You are a real potential client interested in buying a consortium (consórcio imobiliário).

NEVER reveal that you are an AI.

CLIENT PROFILE:
- Name/Type: {profile.name}
- Personality: {profile.personality}
- Objectives: {', '.join(profile.objectives)}

INSTRUCTIONS:
- Respond naturally, like a real person would
- Ask questions and raise concerns/objections
- Be conversational and genuine
- Don't sound robotic or scripted
- Keep your response SHORT: 2-3 sentences maximum. Real conversations are concise.
- If the seller answers well, acknowledge it and move on
- If they don't answer well, press or redirect
"""

    def _build_objection_instruction(self, objection: Objection) -> str:
        variation = objection.variações[0] if objection.variações else objection.objection
        return f"""NEXT OBJECTION (incorporate naturally into your response):
- Core objection: {objection.objection}
- Variant to use: {variation}
- Expected counter techniques: {', '.join(objection.técnicas_esperadas)}

Incorporate this objection naturally in your conversation. Don't make it obvious that you're "reading from a script".
"""

    def _format_conversation_history(self, messages: List[Message]) -> str:
        recent = messages[-10:] if len(messages) > 10 else messages
        history = "CONVERSATION HISTORY:\n"
        for msg in recent:
            role = "Client" if msg.role in ("client", "agent") else "Seller"
            history += f"{role}: {msg.content}\n"
        return history

    def generate_response(
        self,
        profile: Profile,
        objection: Objection,
        conversation_history: List[Message]
    ) -> str:
        system = self._build_system_prompt(profile)
        objection_inst = self._build_objection_instruction(objection)
        history = self._format_conversation_history(conversation_history)

        user_prompt = f"""{history}

{objection_inst}

Your response:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=120,
            system=system,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return message.content[0].text

    def evaluate_vendor_response(
        self,
        vendor_response: str,
        objection: Objection,
        conversation_history: List[Message]
    ) -> Optional[str]:
        """Returns a 3-5 sentence coaching hint in Portuguese, or None on failure."""
        history_text = self._format_conversation_history(conversation_history)

        system = """Você é um avaliador especialista em vendas de consórcios imobiliários.
Analise a resposta do vendedor à objeção do cliente e forneça feedback.

Tom: analítico e direto. Sem elogios vazios. Sem introduções como "Boa tentativa" ou "Interessante".
Tamanho: 3-5 frases objetivas.
Foco: o que faltou tecnicamente, onde a resposta foi vaga, o que o cliente esperava ouvir.
Se a objeção foi bem contornada: reconheça em 1 frase e aponte como reforçar ainda mais.
Responda apenas com o feedback, sem explicações adicionais.
Idioma: português brasileiro."""

        user_prompt = f"""{history_text}

OBJEÇÃO APRESENTADA: {objection.objection}
CATEGORIA: {objection.category}
TÉCNICAS ESPERADAS: {', '.join(objection.técnicas_esperadas)}

RESPOSTA DO VENDEDOR: {vendor_response}

Feedback:"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                system=system,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return message.content[0].text.strip()
        except Exception:
            return None

    def generate_report_analysis(self, session_data: dict) -> Optional[Dict]:
        """Returns structured analysis dict with 4 sections, or None on failure."""
        turns_text = ""
        for i, turn in enumerate(session_data.get("turns", []), 1):
            status = "✓ Contornou" if turn["overcome"] else "✗ Não contornou"
            turns_text += f"\n--- Objeção {i}: {turn['objection']} ({turn['category']}) ---\n"
            turns_text += f"Resposta do vendedor: {turn['vendor_response']}\n"
            turns_text += f"Resultado: {status}\n"

        system = """Você é um avaliador sênior de vendedores de consórcios imobiliários.
Analise a sessão de treinamento e produza um diagnóstico estruturado.

Tom: analítico e direto. Sem enrolação. Sem frases de elogio genérico.
Foco: o que o vendedor precisa melhorar e o que precisa estudar.
Idioma: português brasileiro.

Retorne APENAS um JSON válido com exatamente estas chaves:
{
  "objection_analysis": "análise objeção a objeção — o que foi dito, o que era esperado, o que faltou",
  "product_knowledge": "diagnóstico de conhecimento de produto — onde ficou vago, onde demonstrou saber",
  "behavior_patterns": "padrões de comportamento observados — tendências repetidas como evasivo, genérico, bom em comparações etc.",
  "study_topics": ["tópico 1", "tópico 2", "tópico 3"]
}

study_topics deve ter 3-5 itens concisos e específicos."""

        user_prompt = f"""PERFIL DO CLIENTE SIMULADO: {session_data.get('profile')}
SCORE FINAL: {session_data.get('score', 0):.0f}% ({session_data.get('overcome', 0)}/{session_data.get('total', 0)} objeções contornadas)

TURNOS DA SESSÃO:
{turns_text}

Diagnóstico (JSON):"""

        try:
            message = self.client.messages.create(
                model=self.report_model,
                max_tokens=1200,
                system=system,
                messages=[{"role": "user", "content": user_prompt}]
            )
            raw = message.content[0].text.strip()
            # strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw)
        except Exception:
            return None
