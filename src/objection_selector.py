import random
from typing import Optional
from src.models import Objection, Session
from src.objection_bank import ObjectionBank
from src.profile_system import ProfileSystem


class ObjectionSelector:
    def __init__(self, bank: ObjectionBank, profile_system: ProfileSystem):
        self.bank = bank
        self.profile_system = profile_system

    def select_next(self, session: Session) -> Optional[Objection]:
        """
        Select the next objection for the session.

        Respects the profile's objection priority and prevents duplicates.
        Enforces max 10 objections per session.
        Uses 20% randomness for variety while mostly following priority order.
        """
        if len(session.objections_used) >= 10:
            return None  # Max 10 objections per session

        # Get profile
        profile = self.profile_system.get_by_name(session.profile)
        if not profile:
            return None

        # Get already used objection IDs
        used_ids = {usage.id for usage in session.objections_used}

        # Get priority list for this profile, filter out used
        priority = [
            obj_id for obj_id in profile.objection_priority
            if obj_id not in used_ids
        ]

        if not priority:
            return None

        # Select next from priority (with 20% randomness for variety)
        if random.random() < 0.2 and len(priority) > 1:
            # Pick random from remaining
            selected_id = random.choice(priority)
        else:
            # Pick next in priority
            selected_id = priority[0]

        return self.bank.get_by_id(selected_id)
