from enum import Enum
from pathlib import Path
from datetime import datetime

# TODO: Put these into an Enum
ITEM_DATA_PATH = "./data/items/items.json"
TEMP_IMAGE_DATA_PATH = "./data/images/"
TEMP_AUDIO_DATA_PATH = "./data/audio/"
MAP_DATA_PATH = "./data/environments/map.json"
QUEST_DATA_PATH = "./data/quests/quests.json"
NPC_DATA_PATH = "./data/characters/characters.json"
LOCAL_LOCATIONS_PATH = "./data/environments/local_locations.json"
TRIGGERS_DATA_PATH = "./data/triggers/triggers.json"
ENVIRONMENT_DATA_PATH = "./data/environments/environments.json"
PLAYER_DATA_PATH = "./data/player/player.json"

GAME_DATA_PATH = "./data/game/game.json"

class AgentConfigs(Enum):

    VERBOSE = False

class GameDataPaths:

    def __init__(
            self,
            item_data_path: Path = Path("./data/items/items.json"),
            temp_image_data_path: Path = Path("./data/images/"),
            temp_audio_data_path: Path = Path("./data/audio/"),
            map_data_path: Path = Path("./data/environments/map.json"),
            quest_data_path: Path = Path("./data/quests/quests.json"),
            npc_data_path: Path = Path("./data/characters/characters.json"),
            local_locations_data_path: Path = Path("./data/environments/local_locations.json"),
            triggers_data_path: Path = Path("./data/triggers/triggers.json"),
            environments_data_path: Path = Path("./data/environments/environments.json"),
    ):
        self.item_data_path: Path = item_data_path
        self.temp_image_data_path: Path = temp_image_data_path
        self.temp_audio_data_path: Path = temp_audio_data_path
        self.map_data_path: Path = map_data_path
        self.quest_data_path: Path = quest_data_path
        self.npc_data_path: Path = npc_data_path
        self.local_locations_data_path: Path = local_locations_data_path
        self.triggers_data_path: Path = triggers_data_path
        self.environments_data_path: Path = environments_data_path
        self.logs_path: Path = self._new_logs_path()
    
    def _new_logs_path(
            self,
    )->Path:
        now = datetime.now()
        with open(".data/logs/.log", "w") as file:
            file.write(f"- {now.strftime('%Y%m%d%H%M%S')} - New game created.\n")
        return Path(f".data/logs/{now.strftime('%Y%m%d%H%M%S')}.txt")


class DifficultyConfigs(Enum):
    PREPARE_ATTACK_DC = 50
    ATTACK_DC = 50
    DMG_DC = 50