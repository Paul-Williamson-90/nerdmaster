from src.characters.base import Character
from src.items.base import Item
from src.triggers.base import Trigger
from typing import List
from src.quests.base import QuestLog
from pathlib import Path


class Position:

    def __init__(
            self,
            name: str,
            position_description: str,
            reveal_description: str|None,
            hidden: bool,
            triggers: List[Trigger|None] = [], # Replace with trigger event
    )->None:
        self.name = name
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
            name: str,
            characters: List[str],
            position_description: str,
            reveal_description: str|None,
            hidden: bool,
            triggers: List[Trigger|None] = [] # Replace with trigger event
    )->None:
        super().__init__(
            name=name,
            position_description=position_description, 
            hidden=hidden, 
            reveal_description=reveal_description, 
            triggers=triggers
        )
        self.characters = characters
    
    def get_characters(self):
        return self.characters
    
    
class ObjectPosition(Position):

    def __init__(
            self,
            name: str,
            image: Path,
            object_id: str,
            items: List[Item],
            position_description: str,
            reveal_description: str|None,
            hidden: bool,
            triggers: List[Trigger|None] = [] # Replace with trigger event
    )->None:
        super().__init__(
            name=name,
            position_description=position_description, 
            hidden=hidden, 
            reveal_description=reveal_description, 
            triggers=triggers
        )
        self.items = items
        self.image = image
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

    def reveal_items_and_triggers(
            self,
            quest_log,
            environment,
    ):
        for trigger in self.triggers:
            if trigger:
                if trigger.__class__.__name__ == "InteractTrigger":
                    trigger.prepare(
                        quest_log=quest_log,
                        environment=environment,
                    )
        return self.get_items()
    
    def get_image(self):
        return self.image

