from src.characters.skills.base import Skill
from src.characters.skills.skills import SkillMap, ProficiencyNames
from typing import List, Dict

DEFAULT_SKILL_TREE = {
    "Dexterity": "UNTRAINED",
    "Aim": "UNTRAINED",
    "Athletics": "UNTRAINED",
    "Brawl": "UNTRAINED",
    "Lockpick": "UNTRAINED",
    "Medicine": "UNTRAINED",
    "Mechanics": "UNTRAINED",
    "Computers": "UNTRAINED",
    "Driving": "UNTRAINED",
    "Stealth": "UNTRAINED",
    "Perception": "UNTRAINED",
}

class SkillTree:

    def __init__(
            self,
            skills: List[Skill]|Dict[str, str] = DEFAULT_SKILL_TREE, 
    )->None:
        self.skills = self._unpack_skills(skills)

    def _unpack_skills(
            self,
            skills: List[Skill]|Dict[str, str],
    )->Dict[str, Skill]:
        """
        Unpack the skills.

        Args:
        skills (list): The list of skills.

        Returns:
        Dict[str, Skill]: The unpacked skills.
        """
        if isinstance(skills, dict):
            skills = [SkillMap[skill].value(ProficiencyNames[proficiency]) for skill, proficiency in skills.items()]
        elif isinstance(skills, list):
            skills = skills
        unpacked_skills = dict()
        for skill in skills:
            unpacked_skills[skill.name] = skill
        return unpacked_skills
    
    def get_proficiency(
            self,
            skill: str,
    )->str:
        """
        Get the proficiency of the character.

        Returns:
        str: The proficiency of the character.
        """
        proficiency = self.skills[skill].get_proficiency()
        return proficiency
    
    def get_proficiency_description(
            self,
            name: str,
            skill: str,
    )->str:
        """
        Get the proficiency description of the character.

        Args:
        name (str): The name of the character.

        Returns:
        str: The proficiency description of the character.
        """
        message = self.skills[skill].get_proficiency_description(name)
        return message
    
    def get_modifier(
            self,
            skill: str,
    )->int:
        """
        Get the modifier based on the proficiency level.

        Returns:
        int: The modifier.
        """
        modifier = self.skills[skill].get_modifier()
        return modifier
    
    def increase_proficiency(
            self,
            name: str,
            skill: str,
    )->str:
        """
        Increase the proficiency level.

        Args:
        name (str): The name of the character.

        Returns:
        str: The message.
        """
        message = self.skills[skill].increase_proficiency(name)
        return message
    
    def serialize(
            self,
    )->Dict[str, str]:
        """
        Serialize the skills.

        Returns:
        Dict[str, str]: The serialized skills.
        """
        serialized_skills = {skill: skill.get_proficiency() for skill in self.skills.values()}
        return serialized_skills