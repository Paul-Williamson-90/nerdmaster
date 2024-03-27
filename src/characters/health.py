from enum import Enum
import random
from typing import List

from src.characters.prompts import (
    HEALTH_UPDATE, 
    HEALTH_UPDATE_PRECONDITIONS, 
    GENERATE_SCAR,
    DEATH_PROMPT
)

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
        """
        Get the health status of the character.

        Args:
        name (str): The name of the character.

        Returns:
        str: The health status of the character.
        """
        message = f"{name} {self.status.value}"
        return message
    
    def get_roll_modifier(
            self,
    )->int:
        """
        Get the roll modifier based on the health status.

        Returns:
        int: The roll modifier.
        """
        modifier = HealthDisadvantages[self.status.name].value
        return modifier
    
    def change_health_status_tick(
            self,
            name: str,
            modifier: int = 1,
    )->str:
        """
        Update the health status ticker and check for status updates.

        Args:
        name (str): The name of the character.
        modifier (int): The modifier to apply to the status ticker.

        Returns:
        str: The status update message.
        """
        self.status_turn_count += modifier
        response = self._check_status_tick_update(name)
        return response

    def _check_status_tick_update(
            self,
            name: str,
    )->str:
        """
        Checks for any status updates from the status ticker.

        Args:
        name (str): The name of the character.

        Returns:
        str: The status update message.
        """
        # if injured and getting healthy
        if self.status == HealthDescriptions.INJURED:
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
        # if dying and dead
        elif self.status == HealthDescriptions.DYING:
            if self.status_turn_count >= HealthStatusChangeTick[self.status.name].value:
                self.status_turn_count = 0
                self.status = HealthDescriptions[HealthStatusChange[self.status.name].value]
                return self._generate_death_message(name)
        return ""
    
    def _generate_death_message(
            self,
            name: str,
    )->str:
        """
        Generate a death message for the character.

        Args:
        name (str): The name of the character.

        Returns:
        str: The death message.
        """
        prompt = DEATH_PROMPT.format(
            name=name,
            description=self.description,
        )
        message = self._call_gpt(prompt)
        return message
    
    def _check_scarring(
            self,
            prev_status: HealthDescriptions,
    )->str:
        """
        Roll for scarring based on the previous status.

        Args:
        prev_status (HealthDescriptions): The previous health status.

        Returns:
        str: The scarring message.
        """
        roll = random.randint(1, 100)
        scar = ""
        if prev_status == HealthDescriptions.INJURED:
            if roll < HealthConfig.INJURED_SCARRING_CHANCE.value:
                scar = self._generate_scar()
                self.scars += [scar]
                self.description = ""
        return scar

    def _generate_scar(
            self,
    )->str:
        """
        Generate a scar for the character.

        Returns:
        str: The scar message.
        """
        prompt = GENERATE_SCAR.format(
            description=self.description,
        )
        scar = self._call_gpt(prompt)
        return scar
    
    def _get_health_update_prompt(
            self,
            event_description: str,
            pre_conditions: str|None,
    )->str:
        """
        Generate the health update prompt.

        Args:
        event_description (str): The description of the event.
        pre_conditions (str|None): The preconditions for the event.

        Returns:
        str: The health update prompt.
        """
        prompt = HEALTH_UPDATE_PRECONDITIONS.format(
            pre_conditions=pre_conditions,
            event_description=event_description,
        ) if pre_conditions else HEALTH_UPDATE.format(
            event_description=event_description,
        )
        return prompt
    
    def update_health_status(
            self,
            new_status: HealthDescriptions,
            event_description: str,
    )->str:
        """
        Update the health status of the character.

        Args:
        new_status (HealthDescriptions): The new health status.
        event_description (str): The description of the event.

        Returns:
        str: The updated health description.
        """
        pre_conditions = None
        # if not healthy, add preconditions
        if (self.status != HealthDescriptions.HEALTHY 
            and new_status != HealthDescriptions.HEALTHY):
            pre_conditions = self.description
        self.status_turn_count = 0
        self.status = new_status
        prompt = self._get_health_update_prompt(event_description, pre_conditions)
        self.description = self._call_gpt(prompt)
        return self.description
    
    def _call_gpt(
            self,
            prompt: str,
    )->str:
        """
        Sends a prompt to the GPT-3 API.

        Args:
        prompt (str): The prompt to send to the API.

        Returns:
        str: The response from the API.
        """
        raise NotImplementedError("GPT-3 API call not implemented yet.")