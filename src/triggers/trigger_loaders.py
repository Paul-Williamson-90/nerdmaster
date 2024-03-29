from pathlib import Path
import json
from enum import Enum

from src.triggers.base import Trigger, Dialogue
from src.environments.environment_triggers import TriggerDialogue
from src.configs import TRIGGERS_DATA_PATH

class TriggerTypeMap(Enum):
    dialogue = Dialogue
    trigger_dialogue = TriggerDialogue

class TriggerLoader:
    def __init__(
        self,
        data_path: Path = Path(TRIGGERS_DATA_PATH),
        trigger_type_map: Enum = TriggerTypeMap,
    ):
        self.data_path = data_path
        self.trigger_type_map = trigger_type_map
        self.triggers = self._load_triggers()

    def _load_triggers(self):
        with open(self.data_path, 'r') as file:
            triggers = json.load(file)
        return triggers
    
    def get_trigger(self, trigger_id: str)->Trigger:
        trigger_type = self.triggers[trigger_id]["trigger_type_id"]
        trigger_object = self.trigger_type_map[trigger_type].value
        return trigger_object(**{k:v for k,v in self.triggers[trigger_id].items()
                                 if k not in ["trigger_type_id"]})