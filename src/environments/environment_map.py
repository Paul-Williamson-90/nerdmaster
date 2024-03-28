from typing import Dict

class MapLocation:

    def __init__(
            self,
            location_id: str,
            description: str,
            turns_to_visit: int
    ):
        self.location_id = location_id
        self.description = description
        self.turns_to_visit = turns_to_visit

class EnvironmentMap:

    def __init__(
            self,
            map: Dict[str, MapLocation],
    )->None:
        self.map = map
    