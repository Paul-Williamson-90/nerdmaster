from pathlib import Path
import json
from src.configs import MAP_DATA_PATH

class EnvironmentMap:

    def __init__(
            self,
            current_location: str,
            map_data_path: Path = Path(MAP_DATA_PATH),
    )->None:
        self.current_location = current_location
        self.map_data_path = map_data_path
        self.map = self._load_map()
        self.local_map = self.map[current_location]

    def _load_map(self):
        with open(self.map_data_path, 'r') as file:
            global_map = json.load(file)
        return global_map
    