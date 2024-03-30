from src.triggers.base import Trigger
# from src.characters.base import Character
from src.utils.tools import create_action_tool

from typing import Dict

from abc import ABC, abstractmethod



class ReActionMap(ABC):

    def __init__(
            self,
            character#: Character,
    ):
        self.character = character
        self.action_map: Dict[str, Dict[str, Trigger]] = {}

    def _get_tools(
            self,
            mode: str,
    )->dict:
        tools = dict()
        for k,tool in self.action_map[mode].items():
            tools[k] = create_action_tool(tool, k)
        return tools 
    
    @abstractmethod
    def get_reaction(
            self,
            event: str,
            mode: str,
    ):
        ...