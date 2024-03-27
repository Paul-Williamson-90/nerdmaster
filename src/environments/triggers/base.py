from abc import ABC, abstractmethod

class Trigger(ABC):
    
    def __init__(
            self,
            trigger_id: str,
    ):
        self.trigger_id = trigger_id