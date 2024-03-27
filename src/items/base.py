from src.characters.skills.base import Skill, ProficiencyNames, ProficiencyModifiers
from src.characters.skills.skills import SkillMap
from src.characters.skills.skill_tree import SkillTree
from src.triggers.base import Trigger

from uuid import uuid4

class Item:
    def __init__(
            self, 
            item_id: str,
            name: str, 
            description: str, 
            value: int,
            mass: float,
            equipable: bool = False,
            equip_slot: str|None = None, # TODO: Replace with EquipSlot class
            min_proficiency: ProficiencyNames|str|None = None,
            skill: Skill|dict|None = None,
            trigger: Trigger|None = None,
    )->None:
        self.unique_id = uuid4()
        self.item_id = item_id
        self.name = name
        self.description = description
        self.value = value
        self.mass = mass
        self.equipable = equipable
        self.equip_slot = equip_slot
        self.min_proficiency: ProficiencyNames|None = self._handle_proficiency(min_proficiency)
        self.skill: Skill|None = self._handle_skill(skill)
        self.trigger = trigger

    def _handle_skill(
            self,
            skill: Skill|str|None,
    )->Skill|None:
        if skill is None:
            return None
        if isinstance(skill, dict):
            skill_name = skill.get("name")
            skill_object = SkillMap[skill_name].value
            skill_proficiency = skill.get("proficiency")
            return skill_object(proficiency=skill_proficiency)
        return skill 

    def _handle_proficiency(
            self,
            min_proficiency: ProficiencyNames|str|None,
    )->ProficiencyNames|None:
        if min_proficiency is None:
            return None
        if isinstance(min_proficiency, str):
            return ProficiencyNames[min_proficiency]
        return min_proficiency

    def equip_skill_check(
            self,
            user_skill_tree:SkillTree,
    )->bool:
        if self.skill is None:
            return True
        if self.min_proficiency is not None:
            user_skill = user_skill_tree.get_modifier(self.skill.name)
            if user_skill < ProficiencyModifiers[self.min_proficiency.name].value:
                return False
        return True
    
    def get_modifier(
            self,
    )->int:
        if self.skill is None:
            return 0
        return self.skill.get_modifier()
    
    def get_value(
            self
    )->int:
        return self.value
    
    def get_description(
            self,
    )->str:
        return self.description
    
    def get_name(
            self,
    )->str:
        return self.name
    
    def get_item_id(
            self,
    )->str:
        return self.item_id
    
    def get_unique_id(
            self,
    )->str:
        return self.unique_id
    
    def get_mass(
            self,
    )->float:
        return self.mass

    def __str__(self):
        return f"{self.name}\n{self.description}"