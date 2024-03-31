from pathlib import Path
import json
from enum import Enum

from src.triggers.base import Trigger
from src.triggers.environment_triggers import (
    OnEntryTrigger,
    TurnsInLocationTrigger,
    OnExitTrigger,
    TriggerEventAnyCharacter,
    TriggerEventAllCharacter,
    DescribeLocationTrigger,
    OnRevealTrigger,
    RevealTrigger,
)
from src.game.configs import TRIGGERS_DATA_PATH


class TriggerTypeMap(Enum):

    # Environment Triggers
    OnEntryTrigger = OnEntryTrigger
    TurnsInLocationTrigger = TurnsInLocationTrigger
    OnExitTrigger = OnExitTrigger
    DescribeLocationTrigger = DescribeLocationTrigger

    # Reveals
    OnRevealTrigger = OnRevealTrigger
    RevealTrigger = RevealTrigger

    # Interaction Triggers
    TriggerEventAnyCharacter = TriggerEventAnyCharacter
    TriggerEventAllCharacter = TriggerEventAllCharacter


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
        return trigger_object(
            **{k:v for k,v in self.triggers[trigger_id].items()
                if k not in ["trigger_type_id"]}
        )