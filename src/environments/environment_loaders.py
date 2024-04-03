from src.triggers.trigger_loaders import TriggerLoader
from src.environments.positions import CharacterPosition, ObjectPosition
from src.items.item_loader import ItemLoader
from src.environments.environment_map import EnvironmentMap, MapLocation
from src.environments.local_locations import LocalLocation
from src.environments.base import Environment
from src.game.configs import MAP_DATA_PATH, LOCAL_LOCATIONS_PATH, ENVIRONMENT_DATA_PATH

from enum import Enum
from pathlib import Path
import json

class PositionMapper(Enum):
    character_position = CharacterPosition
    object_position = ObjectPosition



class LocalLocationLoader:

    def __init__(
        self,
        data_path: Path = Path(LOCAL_LOCATIONS_PATH)
    ):
        self.data_path = data_path
        self.local_locations = self._load_local_locations()

    def _load_local_locations(self):
        with open(self.data_path, 'r') as file:
            local_locations = json.load(file)
        return local_locations
    
    def get_local_location(self, location_id: str):
        return LocalLocation(**self.local_locations[location_id])


class EnvironmentMapLoader:

    def __init__(
            self,
            map_data_path: Path = Path(MAP_DATA_PATH),
    )->None:
        self.map_data_path = map_data_path
        self.map = self._load_map()

    def _load_map(self):
        with open(self.map_data_path, 'r') as file:
            global_map = json.load(file)
        return global_map
    
    def get_map_for_location(self, location_id: str):
        map = self.map[location_id]
        map_locations = dict()
        for location_id, location_data in map.items():
            map_locations[location_id]=MapLocation(location_id=location_id, **location_data)
        env_map_data = {"map":map_locations}
        return EnvironmentMap(**env_map_data)

class PositionLoader:

    def __init__(
            self,
            trigger_loader: TriggerLoader = TriggerLoader,
            item_loader: ItemLoader = ItemLoader,
            position_map: Enum = PositionMapper,
    ):
        self.position_map = position_map
        self.item_loader = item_loader
        self.trigger_loader = trigger_loader

    def load_position(
            self,
            position_data: dict,
    ):
        position_type = position_data["position_type_id"]

        if "triggers" in position_data.keys():
            triggers_data = position_data["triggers"]
            triggers = [self.trigger_loader.get_trigger(trigger_id) for trigger_id in triggers_data]
            position_data["triggers"] = triggers

        if "items" in position_data.keys():
            items_data = position_data["items"]
            items = [self.item_loader.get_item(item_id) for item_id in items_data]
            position_data["items"] = items

        if "image" in position_data.keys():
            position_data["image"] = Path(position_data["image"])

        position_object = self.position_map[position_type].value
        return position_object(**{k:v for k,v in position_data.items() if k not in ["position_type_id"]})
    

class EnvironmentLoader:

    def __init__(
            self,
            environment_data_path: Path = Path(ENVIRONMENT_DATA_PATH),
            environment_map_loader: EnvironmentMapLoader = EnvironmentMapLoader,
            location_loader: LocalLocationLoader = LocalLocationLoader,
            position_loader: PositionLoader = PositionLoader,
            trigger_loader: TriggerLoader = TriggerLoader,
    ):
        self.environment_data_path = environment_data_path
        self.environment_data = self._load_environment_data()
        self.environment_map_loader = environment_map_loader
        self.location_loader = location_loader
        self.position_loader = position_loader
        self.trigger_loader = trigger_loader
    
    def _load_environment_data(self):
        with open(self.environment_data_path, 'r') as file:
            environment_data = json.load(file)
        return environment_data
    
    def _get_environment_data(self, location_id: str):
        return self.environment_data[location_id]
    
    def _get_environment_attributes(self, env_data: dict):
        name = env_data["name"]
        description = env_data["description"]
        visual_description = env_data["visual_description"]
        scenario_description_tags = env_data["scenario_description_tags"]
        turns_in_location = env_data["turns_in_location"]
        images = {k: Path(v) if v else v for k,v in env_data["images"].items() }
        return name, description, visual_description, scenario_description_tags, turns_in_location, images
    
    def _get_local_locations(self, env_data: dict):
        local_locations_data = env_data["local_locations"]
        local_locations = []
        for local_location in local_locations_data:
            local_locations.append(
                self.location_loader.get_local_location(local_location)
            )
        return local_locations
    
    def _get_character_locations(self, env_data: dict):
        character_locations_data = env_data["character_locations"]
        character_locations = []
        for character_location in character_locations_data:
            character_locations.append(self.position_loader.load_position(character_location))
        return character_locations
    
    def _get_connecting_locations(self, environment_id: str):
        connecting_locations = self.environment_map_loader.get_map_for_location(environment_id)
        return connecting_locations
    
    def _get_object_locations(self, env_data: dict):
        object_locations_data = env_data["object_locations"]
        object_locations = []
        loader = self.position_loader
        for object_location in object_locations_data:
            object_locations.append(loader.load_position(object_location))
        return object_locations
    
    def _get_triggers(self, env_data: dict):
        trigger_data = env_data["triggers"]
        triggers = []
        loader = self.trigger_loader
        for trigger in trigger_data:
            triggers.append(loader.get_trigger(trigger))
        return triggers
    
    def get_environment(self, environment_id: str):
        env_data = self._get_environment_data(environment_id)
        
        (
            name, 
            description, 
            visual_description, 
            scenario_description_tags, 
            turns_in_location,
            images
         ) = self._get_environment_attributes(env_data)
        
        connecting_locations = self._get_connecting_locations(environment_id)
        local_locations = self._get_local_locations(env_data)
        character_locations = self._get_character_locations(env_data)
        object_locations = self._get_object_locations(env_data)
        triggers = self._get_triggers(env_data)

        environment = Environment(
            location_id=environment_id,
            images=images,
            name=name,
            connecting_locations=connecting_locations,
            local_locations=local_locations,
            character_locations=character_locations,
            description=description,
            visual_description=visual_description,
            scenario_description_tags=scenario_description_tags,
            object_locations=object_locations,
            triggers=triggers,
            turns_in_location=turns_in_location
        )
        return environment