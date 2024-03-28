from typing import List
from src.environments.positions import CharacterPosition, ObjectPosition
from src.environments.local_locations import LocalLocation
from src.environments.environment_map import EnvironmentMap
from src.triggers.base import Trigger


class Environment:

    def __init__(
            self,
            name: str,
            location_id: str,
            connecting_locations: EnvironmentMap, # Replace with location/map
            local_locations: List[LocalLocation], 
            character_locations: List[CharacterPosition], 
            description: str,
            visual_description: str,
            scenario_description_tags: List[str],
            object_locations: List[ObjectPosition],
            triggers: List[Trigger], # Replace with triggers
            turns_in_location: int=0, # Number of turns the player has been here (resets when player leaves location)
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

    def get_character_position_descriptions(self):
        return [character.get_position_description() for character in self.character_locations]

    def get_visual_description(self):
        pass

    def get_description(self):
        return self.description
    
    def add_characters(self, characters: List[CharacterPosition], trigger: Trigger|None=None):
        self.character_locations.extend(characters)
        if trigger:
            pass