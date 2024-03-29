import json
from pathlib import Path

from src.items.base import Item
from src.configs import ITEM_DATA_PATH

class ItemLoader:

    def __init__(
            self,
            data_path: Path = Path(ITEM_DATA_PATH),
    ):
        self.data_path = data_path
        self.items = self._load_items()

    def _load_items(self):
        with open(self.data_path, 'r') as file:
            items = json.load(file)
        return items

    def get_item(self, item_id: str) -> Item:
        return Item(item_id=item_id, **self.items[item_id])