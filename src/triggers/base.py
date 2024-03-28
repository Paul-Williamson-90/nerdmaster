from abc import ABC, abstractmethod
from typing import Dict, Any, List

class Trigger(ABC):
    
    trigger_map: Dict[Any, "Trigger"]
    attributes: Dict[str, Any]

    def get_attributes(self):
        return self.attributes

    @abstractmethod
    def prepare(
    ):
        ...

    @abstractmethod
    def activate(
    ):
        ...

class TriggerResponse:

    triggers: Trigger|List[Trigger]|None = None
    narrative_message: str|None = None
