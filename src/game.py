from pathlib import Path
import json

from src.configs import NEW_GAME_DATA_PATH, GameDataPaths
from src.environments.environment_loaders import (
    EnvironmentLoader, 
    EnvironmentMapLoader, 
    LocalLocationLoader, 
    PositionLoader
)
from src.environments.base import Environment
from src.items.item_loader import ItemLoader
from src.characters.types.npcs.load_npc import NPCLoader
from src.characters.types.player.load_player import PlayerLoader
from src.triggers.trigger_loaders import TriggerLoader
from src.characters.types.player.player import Player

class Game:

    def __init__(
            self,
            # in game data
            player: Player,
            environment: Environment,
            data_paths: GameDataPaths,
            # loaders
            environment_loader: EnvironmentLoader,
            item_loader: ItemLoader,
            npc_loader: NPCLoader,
    ):  
        # loaders
        self.environment_loader: EnvironmentLoader = environment_loader
        self.item_loader: ItemLoader = item_loader
        self.npc_loader: NPCLoader = npc_loader
        # in game data
        self.data_paths: GameDataPaths = data_paths
        self.player: Player = player
        self.environment: Environment = environment





class GameLoader:

    def __init__(
            self,
            player_loader: PlayerLoader=PlayerLoader,
            environment_loader: EnvironmentLoader=EnvironmentLoader,
            environment_map_loader: EnvironmentMapLoader=EnvironmentMapLoader,
            local_location_loader: LocalLocationLoader=LocalLocationLoader,
            position_loader: PositionLoader=PositionLoader,
            trigger_loader: TriggerLoader=TriggerLoader,
            item_loader: ItemLoader=ItemLoader,
    ):
        self.data_paths: GameDataPaths = None
        # loaders
        self.player_loader: PlayerLoader = player_loader()
        self.environment_loader: EnvironmentLoader = environment_loader
        self.environment_map_loader: EnvironmentMapLoader = environment_map_loader
        self.local_location_loader: LocalLocationLoader = local_location_loader
        self.trigger_loader: TriggerLoader = trigger_loader
        self.position_loader: PositionLoader = position_loader
        self.item_loader: ItemLoader = item_loader

    def _load_game_data(
            self,
            game_data_path: Path = Path(NEW_GAME_DATA_PATH)
    ):
        with open(game_data_path, 'r') as f:
            game_data = json.load(f)
        return game_data
    
    def _load_data_paths(
            self,
            game_data: dict
    ):
        data_paths = game_data["data_paths"]
        return GameDataPaths(**data_paths)

    def _setup_environment_loader(
            self,
            data_paths: GameDataPaths
    ):
        return self.environment_loader(
            environment_data_path=data_paths["environments_data_path"],
            environment_map_loader=self.environment_map_loader(map_data_path=Path(data_paths["environment_map_loader"])),
            location_loader=self.local_location_loader(data_path=Path(data_paths["local_locations_data_path"])),
            position_loader=self.position_loader(
                trigger_loader=self.trigger_loader(
                    data_path=Path(data_paths["triggers_data_path"]),
                ),
                item_loader=self.item_loader(
                    data_path=Path(data_paths["item_data_path"]),
                ),
            ),
        )
    
    def _load_player(
            self,
            game_data: dict
    ):
        return self.player_loader.get_player(game_data["player"]["name"])

    def _load_loaders(
            self,
            data_paths: GameDataPaths
    ):
        self.environment_loader = self._setup_environment_loader(data_paths)
        self.item_loader = self.item_loader(data_paths["item_data_path"])
        self.npc_loader = self.npc_loader(data_paths["npc_data_path"])

    def _load_environment(
            self,
            location: str
    ):
        return self.environment_loader.get_environment(location)

    def load_new_game(
            self,
            game_data_path: Path
    ):
        game_data = self._load_game_data(game_data_path)
        data_paths = self._load_data_paths(game_data)
        self._load_loaders(data_paths)
        player = self._load_player(game_data)
        environment = self._load_environment(player.current_location)
        return Game(
            player=player,
            environment=environment,
            data_paths=data_paths,
            environment_loader=self.environment_loader,
            item_loader=self.item_loader,
            npc_loader=self.npc_loader,
        )