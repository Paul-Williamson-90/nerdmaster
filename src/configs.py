from enum import Enum

ITEM_DATA_PATH = "./data/items/items.json"
TEMP_IMAGE_DATA_PATH = "./data/images/temp.png"
TEMP_AUDIO_DATA_PATH = "./data/audio/temp.mp3"
MAP_DATA_PATH = "./data/maps/map.json"
QUEST_DATA_PATH = "./data/quests/quests.json"


class DifficultyConfigs(Enum):
    PREPARE_ATTACK_DC = 50
    ATTACK_DC = 50
    DMG_DC = 50