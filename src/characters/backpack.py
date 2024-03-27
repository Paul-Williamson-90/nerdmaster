from src.inventory_class import InventoryManagement
from src.items.base import Item

class Backpack(InventoryManagement):

    def __init__(
            self,
            item_ids: list[str] = [],
    )->None:
        super().__init__(item_ids=item_ids)

    def get_item_stats(
            self,
            item_id: str,
    )->Item:
        return self._unpack_item(item_id)