import json
from src.configs import QUEST_DATA_PATH


class Quest:
    def __init__(
            self,
            quest_id: str,
    )->None:
        self.quest_id = quest_id

class QuestManager:

    def __init__(
            self,
            quest_data_path: str = QUEST_DATA_PATH,
    ):
        self.quest_data_path = quest_data_path
        self.quests = self.load_quests()
    
    def load_quests(self):
        with open(self.quest_data_path, "r") as f:
            quests = json.load(f)

        loaded_quests = dict()
        for key, quest in quests.items():
            loaded_quests[key] = Quest(**quest)
        return loaded_quests

