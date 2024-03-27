from src.configs import ITEM_DATA_PATH
from src.items.base import Item
from pathlib import Path
import json

class InventoryManagement:

    def __init__(
            self,
            item_data_path: Path = Path(ITEM_DATA_PATH),
            item_ids: list[str] = [],
    )->None:
        self.item_data_path = item_data_path
        self.capacity: float = 1.0
        self.items = self._load_items(item_ids)

    def _get_item_data(
            self,
    )->dict:
        with open(self.item_data_path) as f:
            item_data = json.load(f)
        return item_data

    def _load_items(
            self,
            item_ids: list[str],
    )->list[Item]:
        items = []
        for item_id in item_ids:
            item = self._unpack_item(item_id)
            items.append(item)
            self.capacity -= item.mass
        return items
    
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
    
    def add_item(
            self,
            item_id: str,
    )->None:
        item = self._unpack_item(item_id)
        if self.capacity - item.mass < 0:
            return False, "Not enough capacity"
        self.items.append(item)
        self.capacity -= item.mass
        return True, "Item added"
    
    def remove_item(
            self,
            item_id: str,
    )->None:
        for item in self.items:
            if item.item_id == item_id:
                self.items.remove(item)
                self.capacity += item.mass
                return True, "Item removed"
        return False, "Item not found"