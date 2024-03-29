import json
from src.game.configs import QUEST_DATA_PATH
from typing import List, Dict
from pathlib import Path


class Quest:
    def __init__(
            self,
            quest_id: str,
            name: str,
            description: str,
    )->None:
        self.quest_id = quest_id
        self.name = name
        self.description = description

class QuestLog:

    def __init__(
            self,
            active_quest_ids: List[str],
            completed_quest_ids: List[str],
            completed_trigger_ids: List[str],
    ):
        self.active_quest_ids = active_quest_ids
        self.completed_quest_ids = completed_quest_ids
        self.completed_trigger_ids = completed_trigger_ids

class QuestLoader:

    def __init__(
            self,
            quest_data_path: Path = Path(QUEST_DATA_PATH),
    ):
        self.quest_data_path = quest_data_path
        self.quest_data = self._load_quest_data()
    
    def _load_quest_data(self):
        with open(self.quest_data_path, "r") as f:
            quests = json.load(f)

        loaded_quests = dict()
        for key, quest in quests.items():
            loaded_quests[key] = Quest(quest_id=key, **quest)
        return loaded_quests
    
    def load_quest_log(
            self,
            player_quests: Dict[str, List[str]]
    ):
        active_quest_ids = player_quests["active_quest_ids"]
        completed_quest_ids = player_quests["completed_quest_ids"]
        completed_trigger_ids = player_quests["completed_trigger_ids"]
        return QuestLog(
            active_quest_ids=active_quest_ids,
            completed_quest_ids=completed_quest_ids,
            completed_trigger_ids=completed_trigger_ids
        )

