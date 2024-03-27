from abc import ABC, abstractmethod
from typing import List
import numpy as np

from src.characters.health import Health

class Character(ABC):

    def __init__(
            self,
            name: str,
            inventory: List[str], # TODO: Replace with Item class
            equipped_items: List[str], # TODO: Replace with Item/Equip class
            gold: int,
            background: str, # TODO: Replace with Background class
            memory: str, # TODO: Replace with Memory class
            avatar: np.ndarray|None, # TODO: Replace with Avatar class
            health: Health = Health(),
            with_player: bool = False,
            skills: List[str] = [], # TODO: Replace with Skill class
    )->None:
        self.name = name
        self.inventory = inventory
        self.equipped_items = equipped_items
        self.gold = gold
        self.health = health
        self.background = background
        self.memory = memory
        self.avatar = avatar
        self.with_player = with_player
        self.skills = skills

    @abstractmethod
    def get_agent_tools(self):
        pass