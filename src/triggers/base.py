from abc import ABC, abstractmethod
from typing import List, Dict, Any

class TriggerResponse:

    def __init__(
            self,
            triggers: List[str]|None = None,
            narrative_message: str|None = None,
            attributes: Dict[str, Any]|None = None,
    ):
        self.triggers = triggers
        self.narrative_message = narrative_message
        self.attributes = attributes

class Trigger(ABC):
    
    def __init__(
        self,
        trigger_id: str,
    ):
        self.trigger_id = trigger_id

    @abstractmethod
    def prepare(
    ):
        ...

    @abstractmethod
    def activate(
    )->TriggerResponse:
        ...

