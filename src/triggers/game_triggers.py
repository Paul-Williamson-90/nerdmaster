from typing import Any
from src.triggers.base import Trigger


class Dialogue(Trigger):

    trigger_map = {}

    def prepare(
            self,
            character: Any,
            dialogue: str,
    ):
        self.attributes = {
            "character": character,
            "dialogue": dialogue,
        }
        self.character = character
        self.dialogue = dialogue

        return self

    def activate(
            self,
            character: Any,
            dialogue: str,
    ):
        """
        Game logic for activating the trigger
        Triggers a dialogue from the NPC.
        Triggers are resolved by the Game class, post NPC agent output.
        """
        ...