from abc import ABC, abstractmethod
from typing import List, Dict
import numpy as np

from src.characters.health import Health, DEFAULT_HEALTH
from src.characters.skills.skill_tree import SkillTree, DEFAULT_SKILL_TREE
from src.characters.backpack import Backpack
from src.characters.equipped import Equipped, DEFAULT_SLOT_ITEMS
from src.characters.background import Background

class Character(ABC):

    def __init__(
            self,
            name: str,
            gold: int,
            background: Background|dict,
            visual_description: str,
            memory: str, # TODO: Replace with Memory class
            avatar: np.ndarray|None, # TODO: Replace with Avatar class
            health: Health|dict = DEFAULT_HEALTH,
            skills: SkillTree|Dict[str, str] = DEFAULT_SKILL_TREE,
            backpack: Backpack|List[str] = [], 
            equipped_items: Equipped|Dict[str, str] = DEFAULT_SLOT_ITEMS, 
            with_player: bool = False,
    )->None:
        self.name = name
        self.visual_description = visual_description
        self.backpack = self._handle_backpack(backpack)
        self.equipped_items = self._handle_equipped_items(equipped_items)
        self.gold = gold
        self.health = self._handle_health(health)
        self.background = self._handle_background(background)
        self.memory = memory
        self.avatar = avatar
        self.with_player = with_player
        self.skills = self._handle_skills(skills)

    def _handle_skills(
            self,
            skills: SkillTree|Dict[str, str],
    )->SkillTree:
        if isinstance(skills, SkillTree):
            return skills
        return SkillTree(skills=skills)

    def _handle_health(
            self,
            health: Health|dict,
    )->Health:
        if isinstance(health, Health):
            return health
        return Health(**health)

    def _handle_background(
            self,
            background: Background|dict,
    )->Background:
        if isinstance(background, Background):
            return background
        return Background(**background)

    def add_item_to_backpack(
            self,
            item_id: str
    )->str:
        status, message = self.backpack.add_item(item_id)
        message += " backpack"
        return message
    
    def remove_item_from_backpack(
            self,
            item_id: str
    )->str:
        status, message = self.backpack.remove_item(item_id)
        message += " backpack"
        return message
    
    def _equip_item_checks(
            self,
            item_id: str,
    )->tuple[bool, str]:
        if item_id not in [x.item_id for x in self.backpack.items]:
            return False, "Item not in backpack"
        # equipable
        item_stats = self.backpack.get_item_stats(item_id)
        if not item_stats.equipable:
            return False, "Item not equipable"
        # skill check
        if not item_stats.equip_skill_check(self.skills):
            return False, "Insufficient proficiency to equip item"
        # mass check
        slot = item_stats.equip_slot
        mass = item_stats.mass
        equipped_item_id = self.equipped_items.get_equipped_item_id_by_slot(slot)
        if equipped_item_id:
            equipped_item = self.backpack.get_item_stats(equipped_item_id)
            if not self.backpack.add_item_mass_check(equipped_item, mass):
                return False, "Not enough capacity in backpack to unequip item in replace of item to equip"
        return True, ""
    
    def equip_item(
            self,
            item_id: str
    )->str:
        status, message = self._equip_item_checks(item_id)
        if not status:
            return message
        status, message, id_unequipped = self.equipped_items.equip_item(item_id)
        if id_unequipped:
            self.add_item_to_backpack(id_unequipped)
        status, message = self.backpack.remove_item(item_id)
        message += " equipped items"
        return message
    
    def unequip_item(
            self,
            slot: str
    )->str:
        equipped_item_id = self.equipped_items.get_equipped_item_id_by_slot(slot)
        if not equipped_item_id:
            return "No item equipped in slot"
        equipped_item = self.backpack.get_item_stats(equipped_item_id)
        equipped_item_mass = equipped_item.mass
        if not self.backpack.add_item_mass_check(equipped_item_mass):
            return "Not enough capacity in backpack to unequip item"
        status, message, id_unequipped = self.equipped_items.unequip_item(slot)
        if id_unequipped:
            message+=self.add_item_to_backpack(id_unequipped)
        return message

    def modify_gold(
            self, 
            amount: int
    )->tuple[bool, str]:
        updated_gold = self.gold + amount
        if updated_gold < 0:
            return False, "Insufficient gold"
        self.gold = updated_gold
        return True, f"{amount} gold added, {self.name} now has {updated_gold} gold"

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
    
    def get_background_full(self):
        return self.background.__str__()
    
    def get_factions(self):
        return self.background.get_factions()
    
    def check_faction(self, faction: str):
        if faction in self.get_factions():
            return True
        return False
    
    def get_backstory(self):
        return self.background.get_backstory()
    
    def get_personality(self):
        return self.background.get_personality()
    
    def get_views_beliefs(self):
        return self.background.get_views_beliefs()
    
    def add_to_factions(self, addition: str):
        return self.background.add_to_factions(addition)
    
    def remove_from_factions(self, addition: str):
        return self.background.remove_from_factions(addition)

    @abstractmethod
    def get_agent_tools(self):
        pass