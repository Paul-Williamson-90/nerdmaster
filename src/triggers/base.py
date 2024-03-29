from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.game.game import Game

class TriggerResponse:

    def __init__(
            self,
            triggers: List[str]|None = None,
            narrative_message: str|None = None,
            attributes: Dict[str, Any]|None = None,
            log_message: str|None = None,
    ):
        self.triggers = triggers
        self.narrative_message = narrative_message
        self.attributes = attributes
        self.log_message = log_message

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
        self,
        game: Game
    )->TriggerResponse:
        ...

