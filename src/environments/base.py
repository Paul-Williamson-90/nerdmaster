from typing import List
from src.environments.positions import CharacterPosition, ObjectPosition
from src.environments.local_locations import LocalLocation
from src.environments.environment_map import EnvironmentMap
from src.triggers.base import Trigger
from src.quests.base import QuestLog


class Environment:

    def __init__(
            self,
            name: str,
            location_id: str,
            connecting_locations: EnvironmentMap, 
            local_locations: List[LocalLocation], 
            character_locations: List[CharacterPosition], 
            description: str,
            visual_description: str,
            scenario_description_tags: List[str],
            object_locations: List[ObjectPosition],
            triggers: List[Trigger], 
            turns_in_location: int = 0, # Number of turns the player has been here (resets when player leaves location)
    )->None:
        self.name = name
        self.location_id = location_id
        self.connecting_locations = connecting_locations
        self.local_locations = local_locations
        self.character_locations = character_locations
        self.description = description
        self.visual_description = visual_description
        self.scenario_description_tags = scenario_description_tags
        self.object_locations = object_locations
        self.triggers = triggers
        self.turns_in_location = turns_in_location
        self.armed_triggers: List[Trigger] = []
        self.object_of_interest: ObjectPosition|None = None

    def add_turn(self):
        self.turns_in_location += 1

    def get_object_of_interest(self):
        return self.object_of_interest
    
    def add_object_of_interest(self, object_name: str):
        for object in self.object_locations:
            if object.name == object_name:
                self.object_of_interest = object
                break

    def get_character_position_descriptions(self):
        return [character.get_position_description() for character in self.character_locations]
    
    def get_object_position_descriptions(self):
        return [object.get_position_description() for object in self.object_locations]
    
    def get_exploration_description(self):
        visual_description = self.get_visual_description()
        characters = self.get_character_position_descriptions()
        objects = self.get_object_position_descriptions()
        return {
            "visual_description": visual_description,
            "character_descriptions": characters,
            "object_descriptions": objects,
        }

    def get_visual_description(self):
        return self.visual_description

    def get_description(self):
        return self.description
    
    def arm_trigger(
            self,
            trigger: Trigger,
    ):
        self.armed_triggers.append(trigger)

    def _reveal_trigger_parse(
            self,
            trigger: Trigger,
            quest_log: QuestLog,
    ):
        if trigger.__class__.__name__ == "RevealTrigger":
            print("Attempting to arm trigger: ", trigger.trigger_id)
            trigger.prepare(
                quest_log=quest_log,
                environment=self,
            )

    def arm_reveal_triggers(
            self,
            quest_log: QuestLog,
    )->List[Trigger]:
        
        for trigger in self.triggers:
            self._reveal_trigger_parse(
                trigger=trigger,
                quest_log=quest_log,
            )
        for location in self.local_locations:
            loc_triggers = location.triggers
            for trigger in loc_triggers:
                self._reveal_trigger_parse(
                    trigger=trigger,
                    quest_log=quest_log,
                )
        for location in self.character_locations:
            loc_triggers = location.triggers
            for trigger in loc_triggers:
                self._reveal_trigger_parse(
                    trigger=trigger,
                    quest_log=quest_log,
                )
        for location in self.object_locations:
            loc_triggers = location.triggers
            for trigger in loc_triggers:
                self._reveal_trigger_parse(
                    trigger=trigger,
                    quest_log=quest_log,
                )
        # armed_triggers = self.armed_triggers
        # self.armed_triggers = []
        # return armed_triggers

    def fetch_reveal_triggers(
            self,
            quest_log: QuestLog,
    )->List[Trigger]:
        
        for trigger in self.triggers:
            self._reveal_trigger_parse(
                trigger=trigger,
                quest_log=quest_log,
            )
        for location in self.local_locations:
            loc_triggers = location.triggers
            for trigger in loc_triggers:
                self._reveal_trigger_parse(
                    trigger=trigger,
                    quest_log=quest_log,
                )
        for location in self.character_locations:
            loc_triggers = location.triggers
            for trigger in loc_triggers:
                self._reveal_trigger_parse(
                    trigger=trigger,
                    quest_log=quest_log,
                )
        for location in self.object_locations:
            loc_triggers = location.triggers
            for trigger in loc_triggers:
                self._reveal_trigger_parse(
                    trigger=trigger,
                    quest_log=quest_log,
                )
        armed_triggers = self.armed_triggers
        self.armed_triggers = []
        return armed_triggers
    
    def fetch_active_triggers(
            self,
            quest_log: QuestLog,
    )->List[Trigger]:
        for trigger in self.triggers:
            if trigger.__class__.__name__ not in ["RevealTrigger"]:
                print("Attempting to arm trigger: ", trigger.trigger_id)
                trigger.prepare(
                    quest_log=quest_log,
                    environment=self,
                )
        armed_triggers = self.armed_triggers
        self.armed_triggers = []
        return armed_triggers
    
    def get_revealed(self):
        revealed = []
        for loc in self.character_locations:
            if loc.hidden is False:
                revealed.append(
                    self._get_revealed(loc)
                )
    
        for loc in self.object_locations:
            if loc.hidden is False:
                revealed.append(
                    self._get_revealed(loc)
                )
        return revealed
    
    def _get_revealed(
            self,
            loc: ObjectPosition|CharacterPosition
    ):
        return {
            "name": loc.name,
            "description": loc.position_description,
            "type": str(loc.__class__.__name__)
        }

    # def add_characters(self, characters: List[CharacterPosition], trigger: Trigger|None=None):
    #     self.character_locations.extend(characters)
    #     if trigger:
    #         pass