from src.game.game import Game
from src.game.configs import GAME_DATA_PATH, GameDataPaths
from src.environments.environment_loaders import (
    EnvironmentLoader, 
    EnvironmentMapLoader, 
    LocalLocationLoader, 
    PositionLoader
)
from src.quests.base import QuestLoader
from src.items.item_loader import ItemLoader
from src.characters.types.npcs.load_npc import NPCLoader
from src.characters.types.player.load_player import PlayerLoader
from src.triggers.trigger_loaders import TriggerLoader

from pathlib import Path
import os
import json

class GameLoader:

    def __init__(
            self,
            game_data_path: Path=Path(GAME_DATA_PATH),
            player_loader: PlayerLoader=PlayerLoader,
            environment_loader: EnvironmentLoader=EnvironmentLoader,
            environment_map_loader: EnvironmentMapLoader=EnvironmentMapLoader,
            local_location_loader: LocalLocationLoader=LocalLocationLoader,
            position_loader: PositionLoader=PositionLoader,
            trigger_loader: TriggerLoader=TriggerLoader,
            item_loader: ItemLoader=ItemLoader,
            npc_loader: NPCLoader=NPCLoader,
            quest_loader: QuestLoader=QuestLoader,
    ):
        self.game_data_path: Path = game_data_path
        self.data_paths: GameDataPaths = None
        # loaders
        self.player_loader: PlayerLoader = player_loader
        self.environment_loader: EnvironmentLoader = environment_loader
        self.environment_map_loader: EnvironmentMapLoader = environment_map_loader
        self.local_location_loader: LocalLocationLoader = local_location_loader
        self.trigger_loader: TriggerLoader = trigger_loader
        self.position_loader: PositionLoader = position_loader
        self.item_loader: ItemLoader = item_loader
        self.npc_loader: NPCLoader = npc_loader
        self.quest_loader: QuestLoader = quest_loader

    def _load_game_data(
            self
    ):
        with open(self.game_data_path, 'r') as f:
            game_data = json.load(f)
        return game_data
    
    def _load_data_paths(
            self,
            game_data: dict,
            player_id: str
    ):
        data_paths = game_data[player_id]
        return GameDataPaths(**data_paths)

    def _setup_environment_loader(
            self,
            data_paths: GameDataPaths
    ):
        return self.environment_loader(
            environment_data_path=data_paths.environments_data_path,
            environment_map_loader=self.environment_map_loader,
            location_loader=self.local_location_loader,
            position_loader=self.position_loader,
            trigger_loader=self.trigger_loader,
            )
        
    
    def _load_player(
            self,
            player_id: str
    ):
        return self.player_loader.get_player(player_id)

    def _load_loaders(
            self,
            data_paths: GameDataPaths
    ):
        self.trigger_loader = self.trigger_loader(
            data_path=data_paths.triggers_data_path
        )
        
        self.quest_loader = self.quest_loader(
            quest_data_path=data_paths.quest_data_path
        )

        self.player_loader = self.player_loader(
            player_data_path = data_paths.player_data_path,
            trigger_loader=self.trigger_loader,
            quest_loader=self.quest_loader,
            memories_root_dir=data_paths.memories_root_dir
        )

        self.item_loader = self.item_loader(
            data_paths.item_data_path
        )

        self.npc_loader = self.npc_loader(
            data_paths.npc_data_path,
            memories_root_dir=data_paths.memories_root_dir
        )

        self.position_loader = self.position_loader(
            trigger_loader=self.trigger_loader,
            item_loader=self.item_loader,
        )

        self.local_location_loader = self.local_location_loader(
            data_paths.local_locations_data_path
        )

        self.environment_map_loader = self.environment_map_loader(
            data_paths.map_data_path
        )

        self.environment_loader = self._setup_environment_loader(data_paths)

    def _load_environment(
            self,
            location: str
    ):
        return self.environment_loader.get_environment(location)

    def load_game(
            self,
            player_id: str,
    ):
        game_data = self._load_game_data()
        data_paths = self._load_data_paths(game_data, player_id)
        self._load_loaders(data_paths)
        player = self._load_player(player_id)
        environment = self._load_environment(player.current_location)
        return Game(
            player=player,
            environment=environment,
            data_paths=data_paths,
            environment_loader=self.environment_loader,
            item_loader=self.item_loader,
            npc_loader=self.npc_loader,
            trigger_loader=self.trigger_loader,
        )
    
    def _setup_data_paths(
            self,
            player_id: str,
    
    ):
        with open(f".data/game/game_data.json", 'r') as f:
            data = json.load(f)

        if player_id in data.keys():
            raise ValueError(f"Player with id {player_id} already exists.")

        dirs_to_copy = [
        "./data/audio",
        "./data/characters",
        "./data/images",
        "./data/quests",
        ]

        os.mkdir("./saves/" + player_id.replace(" ", "_"))
        for dir in dirs_to_copy:
            os.system(f"cp {dir} ./saves/{player_id.replace(' ', '_')}")
        
        os.mkdir("./saves/" + player_id.replace(" ", "_") + "/memories")
        
        data_paths = {
            "item_data_path" : "./data/items/items.json",
            "temp_image_data_path" : "./saves/" + player_id.replace(" ", "_")+"/images/",
            "temp_audio_data_path" : "./saves/" + player_id.replace(" ", "_")+"/audio/",
            "map_data_path" : "./data/environments/map.json",
            "quest_data_path" : "./saves/" + player_id.replace(" ", "_")+"/quests/quests.json",
            "npc_data_path" : "./saves/" + player_id.replace(" ", "_")+"/characters/characters.json",
            "local_locations_data_path" : "./data/environments/local_locations.json",
            "triggers_data_path" : "./data/triggers/triggers.json",
            "environments_data_path" : "./data/environments/environments.json",
            "memories_root_dir": "./saves/" + player_id.replace(" ", "_") + "/memories/",
        }

        data[player_id] = data_paths["data_paths"]

        with open(f".data/game/game_data.json", 'w') as f:
            json.dump(data, f)

    def new_game(
            self,
            player_id: str,
    ):
        self._setup_data_paths(player_id)
        return self.load_game(player_id)
        