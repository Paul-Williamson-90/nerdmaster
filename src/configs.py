from enum import Enum

ITEM_DATA_PATH = "./data/items/items.json"
TEMP_IMAGE_DATA_PATH = "./data/images/temp.png"
TEMP_AUDIO_DATA_PATH = "./data/audio/temp.mp3"
MAP_DATA_PATH = "./data/environments/map.json"
QUEST_DATA_PATH = "./data/quests/quests.json"
NPC_DATA_PATH = "./data/characters/characters.json"
LOCAL_LOCATIONS_PATH = "./data/environments/local_locations.json"
TRIGGERS_DATA_PATH = "./data/triggers/triggers.json"
ENVIRONMENT_DATA_PATH = "./data/environments/environments.json"


class DifficultyConfigs(Enum):
    PREPARE_ATTACK_DC = 50
    ATTACK_DC = 50
    DMG_DC = 50