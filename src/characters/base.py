from abc import ABC, abstractmethod
from typing import List, Dict
import numpy as np

from src.characters.health import Health
from src.characters.skills.skill_tree import SkillTree
from src.characters.backpack import Backpack
from src.characters.equipped import Equipped

class Character(ABC):

    def __init__(
            self,
            name: str,
            backpack: Backpack|List[str], 
            equipped_items: Equipped|Dict[str, str], 
            gold: int,
            background: str, # TODO: Replace with Background class
            memory: str, # TODO: Replace with Memory class
            avatar: np.ndarray|None, # TODO: Replace with Avatar class
            health: Health = Health(),
            skills: SkillTree = SkillTree(),
            with_player: bool = False,
    )->None:
        self.name = name
        self.backpack = self._handle_backpack(backpack)
        self.equipped_items = self._handle_equipped_items(equipped_items)
        self.gold = gold
        self.health = health
        self.background = background
        self.memory = memory
        self.avatar = avatar
        self.with_player = with_player
        self.skills = skills

    def _handle_equipped_items(
            self,
            equipped_items: Equipped|Dict[str, str],
    )->Equipped:
        if isinstance(equipped_items, Equipped):
            return equipped_items
        return Equipped(slot_items=equipped_items)

    def _handle_backpack(
            self,
            backpack: Backpack|List[str],
    )->Backpack:
        if isinstance(backpack, Backpack):
            return backpack
        return Backpack(item_ids=backpack)

    @abstractmethod
    def get_agent_tools(self):
        pass