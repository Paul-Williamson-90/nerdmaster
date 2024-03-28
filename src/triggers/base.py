from abc import ABC, abstractmethod
from typing import Dict, Any, List

class Trigger(ABC):
    
    trigger_map: Dict[Any, "Trigger"]
    attributes: Dict[str, Any]

    def get_attributes(self):
        return self.attributes

    @abstractmethod
    def prepare(
    ):
        ...

    @abstractmethod
    def activate(
    ):
        ...

class TriggerResponse:

    def __init__(
            self,
            triggers: Trigger|List[Trigger]|None = None,
            narrative_message: str|None = None,
    ):
        self.triggers = triggers
        self.narrative_message = narrative_message


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