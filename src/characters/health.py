from enum import Enum
import random
from typing import List

class HealthConfig(Enum):
    INJURED_SCARRING_CHANCE: int = 10
    DYING_SCARRING_CHANCE: int = 50
    STATUS_MOVEMENT_MESSAGE: str = "{name} is no longer {old_status} and {new_status}"

class HealthDescriptions(Enum):
    HEALTHY: str = "is healthy."
    INJURED: str = "is injured, but recovering."
    DYING: str = "is dying, they need healing soon or they will die!"
    DEAD: str = "is dead."

class HealthDisadvantages(Enum):
    HEALTHY: int = 0
    INJURED: int = -1
    DYING: int = -2
    DEAD: int = -3

class HealthStatusChangeTick(Enum):
    HEALTHY: int = 0
    INJURED: int = 3
    DYING: int = 5
    DEAD: int = 0

class HealthStatusChange(Enum):
    HEALTHY: str = "HEALTHY"
    INJURED: str = "HEALTHY"
    DYING: str = "DEAD"
    DEAD: str = "DEAD"

class Health:

    def __init__(
            self,
            status: HealthDescriptions = HealthDescriptions.HEALTHY,
            status_turn_count: int = 0,
            description: str = "",
            scars: List[str|None] = [],
    )->None:
        self.status = status
        self.status_turn_count = status_turn_count
        self.description = description
        self.scars = scars

    def get_health_status(
            self,
            name: str,
    )->str:
        message = f"{name} {self.status.value}"
        return message
    
    def get_roll_modifier(
            self,
    )->int:
        modifier = HealthDisadvantages[self.status.name].value
        return modifier
    
    def change_health_status_tick(
            self,
            name: str,
            modifier: int = 1,
    )->None:
        self.status_turn_count += modifier
        self._check_status_tick_update(name)

    def _check_status_tick_update(
            self,
            name: str,
    )->str:
        if self.status_turn_count >= HealthStatusChangeTick[self.status.name].value:
            self.status_turn_count = 0
            prev_status = self.status
            self.status = HealthDescriptions[HealthStatusChange[self.status.name].value]
            scar = self._check_scarring(prev_status)
            message = HealthConfig.STATUS_MOVEMENT_MESSAGE.value.format(
                name=name,
                old_status=prev_status.value,
                new_status=self.status.value,
            )
            formatted_message = f"{message}\n{scar}"
            return formatted_message
        return ""
    
    def _check_scarring(
            self,
            prev_status: HealthDescriptions,
    )->None:
        roll = random.randint(1, 100)
        scar = ""
        if prev_status == HealthDescriptions.INJURED:
            if roll < HealthConfig.INJURED_SCARRING_CHANCE.value:
                scar = self._generate_scar()
                self.scars += [scar]
        elif prev_status == HealthDescriptions.DYING:
            if roll < HealthConfig.DYING_SCARRING_CHANCE.value:
                scar = self._generate_scar()
                self.scars += [scar]
        return scar

    def _generate_scar(
            self,
    )->str:
        scar = "Scar" # TODO: Replace with GPT generated scar using self.description
        self.description = ""
        return scar