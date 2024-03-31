from src.characters.base import Character
from src.items.base import Item
from src.triggers.base import Trigger
from typing import List


class Position:

    def __init__(
            self,
            position_description: str,
            reveal_description: str|None,
            hidden: bool,
            triggers: List[Trigger|None] = [], # Replace with trigger event
    )->None:
        self.position_description = position_description
        self.hidden = hidden
        self.reveal_description = reveal_description
        self.triggers = triggers

    def get_position_description(self):
        return self.position_description
    
    def get_reveal_description(self):
        return self.reveal_description


class CharacterPosition(Position):

    def __init__(
            self,
            characters: List[str],
            position_description: str,
            activity_description: str,
            reveal_description: str|None,
            hidden: bool,
            triggers: List[Trigger|None] = [] # Replace with trigger event
    )->None:
        super().__init__(position_description, hidden, reveal_description, triggers)
        self.characters = characters
        self.activity_description = activity_description
    
    def get_activity_description(self):
        return self.activity_description
    
    def get_characters(self):
        return self.characters
    
    
class ObjectPosition(Position):

    def __init__(
            self,
            object_id: str,
            items: List[str],
            position_description: str,
            reveal_description: str|None,
            hidden: bool,
            triggers: List[Trigger|None] = [] # Replace with trigger event
    )->None:
        super().__init__(position_description, hidden, reveal_description, triggers)
        self.items = items
        self.object_id = object_id

    def get_items(self):
        return self.items
    
    def take_item(self, item_id: str):
        if item_id in [item.item_id for item in self.items]:
            self.items = [item for item in self.items if item.item_id != item_id]
            trigger = self._check_trigger(item_id)
            return item_id, trigger
        return None
    
    def _check_trigger(self, item_id: str):
        # TODO: Implement trigger check
        pass

