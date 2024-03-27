from src.characters.skills.base import Skill, ProficiencyNames, ProficiencyModifiers
from src.characters.skills.skill_tree import SkillTree

class Item:
    def __init__(
            self, 
            item_id: str,
            name: str, 
            description: str, 
            value: int,
            equipable: bool = False,
            equip_slot: str|None = None, # TODO: Replace with EquipSlot class
            min_proficiency: ProficiencyNames|None = None,
            skill: Skill|None = None,
    )->None:
        self.item_id = item_id
        self.name = name
        self.description = description
        self.value = value
        self.equipable = equipable
        self.equip_slot = equip_slot
        self.min_proficiency = min_proficiency
        self.skill = skill

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
    
    def get_id(
            self,
    )->str:
        return self.item_id

    def __str__(self):
        return f"{self.name}\n{self.description}"