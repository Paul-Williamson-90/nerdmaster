from enum import Enum
from typing import Dict
from pathlib import Path
import json

from src.items.base import Item
from src.configs import ITEM_DATA_PATH
from src.characters.skills.skill_tree import SkillTree

class EquipSlotName(Enum):
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"

DEFAULT_SLOT_ITEMS = {k: None for k in EquipSlotName.__members__.keys()}

class Equipped:
    def __init__(
            self,
            item_data_path: Path = Path(ITEM_DATA_PATH),
            slot_items: Dict[str, str] = DEFAULT_SLOT_ITEMS,
    )->None:
        self.item_data_path = item_data_path
        self.equipped = self._handle_slot_items(slot_items)

    def equip_item(
            self,
            item_id: str,
            skill_tree: SkillTree,
    )->tuple[bool, str, str]:
        item = self._unpack_item(item_id)
        if item.equipable is False:
            return False, f"{item.name} is not equipable", None
        if not item.equip_skill_check(skill_tree):
            return False, f"Insufficient proficiency to equip {item.name}", None
        slot = item.equip_slot
        if self.equipped[slot]:
            name_unequipped, id_unequipped = self.unequip_item(slot)
            self.equipped[slot] = item
            return True, f"{item.name} equipped in replace of {name_unequipped}", id_unequipped
        self.equipped[slot] = item
        return True, f"{item.name} equipped", None
    
    def unequip_item(
            self,
            slot: str,
    )->tuple[str, str]:
        item = self.equipped[slot]
        self.equipped[slot] = None
        return item.name, item.item_id

    def _handle_slot_items(
            self,
            slot_items: Dict[str, str],
    )->Dict[str, Item]:
        equipped = {}
        for slot, item_id in slot_items.items():
            equipped[slot] = self._unpack_item(item_id)
        return equipped

    def _get_item_data(
            self,
    )->dict:
        with open(self.item_data_path) as f:
            item_data = json.load(f)
        return item_data
            
    def _unpack_item(
            self,
            item_id: str,
    )->Item:
        item_data = self._get_item_data()
        item = item_data[item_id]
        return Item(
            item_id=item_id,
            name=item["name"],
            description=item["description"],
            value=item["value"],
            mass=item["mass"],
            equipable=item["equipable"],
            equip_slot=item["equip_slot"],
            min_proficiency=item["min_proficiency"],
            skill=item["skill"],
        )
    
    def get_equipped_items(
            self,
    )->Dict[str, str]:
        return {k: v.__str__ if v else None for k, v in self.equipped.items()}
    
    def get_equipped_item_modifier(
            self,
            slot: str,
    )->int:
        item = self.equipped[slot]
        return item.get_modifier() if item else 0