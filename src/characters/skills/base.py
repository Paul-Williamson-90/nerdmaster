from enum import Enum

class ProficiencyModifiers(Enum):
    UNTRAINED: int = 0
    TRAINED: int = 1
    EXPERT: int = 2
    MASTER: int = 3

class ProficiencyNames(Enum):
    UNTRAINED: str = "untrained"
    TRAINED: str = "trained"
    EXPERT: str = "expert"
    MASTER: str = "master"

class ProficiencyUpskillMap(Enum):
    UNTRAINED: str = "trained"
    TRAINED: str = "expert"
    EXPERT: str = "master"
    MASTER: str = "master"

class Skill:

    def __init__(
            self,
            name: str,
            description: str,
            proficiency: ProficiencyNames = ProficiencyNames.UNTRAINED,
    )->None:
        self.name = name
        self.description = description
        self.proficiency = proficiency

    def get_proficiency(
            self,
    )->str:
        """
        Get the proficiency of the character.
        
        Returns:
        str: The proficiency of the character.
        """
        return self.proficiency.value

    def get_proficiency_description(
            self,
            name: str,
    )->str:
        """
        Get the proficiency description of the character.
        
        Args:
        name (str): The name of the character.
        
        Returns:
        str: The proficiency description of the character.
        """
        message = f"{name} is {self.proficiency.value} in {self.name}."
        return message
    
    def get_modifier(
            self,
    )->int:
        """
        Get the modifier based on the proficiency level.
        
        Returns:
        int: The modifier.
        """
        modifier = ProficiencyModifiers[self.proficiency.name].value
        return modifier
    
    def increase_proficiency(
            self,
            name: str,
    )->None:
        """
        Increase the proficiency level.

        Args:
        name (str): The name of the character.

        Returns:
        str: The message.
        """
        if self.proficiency == ProficiencyNames.MASTER:
            return ""
        self.proficiency = ProficiencyUpskillMap[self.proficiency.name]
        message = f"{name} has increased their proficiency in {self.name} to {self.proficiency.value}."
        return message