from src.triggers.base import Trigger

class LocalLocation:

    def __init__(
            self,
            name: str,
            visual_description: str,
            description: str,
            hidden: bool,
            triggers: Trigger|None,
    )->None:
        self.name = name
        self.visual_description = visual_description
        self.description = description
        self.hidden = hidden
        self.triggers = triggers

    def get_visual_description(self):
        return self.visual_description
    
    def get_description(self):
        return self.description
    
    def get_name(self):
        return self.name
    
    def _check_trigger(self):
        pass

    def enter(self):
        pass