from typing import List
from src.models import Profile, Objection, Message
import anthropic

class ClaudeAgent:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-haiku-4-5-20251001"

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
        # Take last 10 messages for context
        recent = messages[-10:] if len(messages) > 10 else messages

        history = "CONVERSATION HISTORY:\n"
        for msg in recent:
            role = "Client" if msg.role == "agent" else "Seller"
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
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        return message.content[0].text
