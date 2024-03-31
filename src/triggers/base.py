from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

class TriggerResponse:

    def __init__(
            self,
            triggers: List[str]|None = None,
            narrative_message: str|None = None,
            attributes: Dict[str, Any]|None = None,
            log_message: str|None = None,
            log_path: Path = None,
    ):
        self.triggers = triggers
        self.narrative_message = narrative_message
        self.attributes = attributes
        self.log_message = log_message
        if log_path:
            self._log_message(log_path)

    def _log_message(
            self,
            log_path: Path,
    ):
        now = datetime.now()
        log_message = f"- {now.strftime('%Y%m%d%H%M%S')} - {self.log_message}\n"
        with open(log_path, "a") as file:
            file.write(log_message)
        

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
        game,
    )->TriggerResponse:
        ...

