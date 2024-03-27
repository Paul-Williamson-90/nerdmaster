from src.inventory_class import InventoryManagement

class Backpack(InventoryManagement):

    def __init__(
            self,
            item_ids: list[str] = [],
    )->None:
        super().__init__(item_ids=item_ids)