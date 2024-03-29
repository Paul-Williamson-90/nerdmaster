from src.configs import GameDataPaths
from src.environments.environment_loaders import (
    EnvironmentLoader, 
)
from src.environments.base import Environment
from src.items.item_loader import ItemLoader
from src.characters.types.npcs.load_npc import NPCLoader
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
        self.game_mode: str = "explore"

    def save_game(self):
        # TODO: Implement save game
        pass

    def fetch_triggers_environment(self):
        quest_log = self.player.quest_log
        prepared_triggers = self.environment_loader.get_active_triggers(
            quest_log = quest_log
        )
        return prepared_triggers

    def turn(
            self,
    ):
        # fetch triggers
        prepared_triggers = self.fetch_triggers()
        # reconcile prepared triggers 




