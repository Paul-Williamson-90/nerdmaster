from src.characters.skills.base import Skill, ProficiencyNames
from enum import Enum


class Dexterity(Skill):

    def __init__(
            self,
            proficiency: ProficiencyNames = ProficiencyNames.UNTRAINED,
    )->None:
        super().__init__(
            name="Dexterity",
            description="Dexterity is a measure of agility, reflexes, and balance.",
            proficiency=proficiency,
        )

class Aim(Skill):

    def __init__(
            self,
            proficiency: ProficiencyNames = ProficiencyNames.UNTRAINED,
    )->None:
        super().__init__(
            name="Aim",
            description="Aim is a measure of how well you can shoot a blaster to hit a target.",
            proficiency=proficiency,
        )

class Athletics(Skill):

    def __init__(
            self,
            proficiency: ProficiencyNames = ProficiencyNames.UNTRAINED,
    )->None:
        super().__init__(
            name="Athletics",
            description="Athletics is a measure of how well you can run, jump, and climb.",
            proficiency=proficiency,
        )

class Brawl(Skill):

    def __init__(
            self,
            proficiency: ProficiencyNames = ProficiencyNames.UNTRAINED,
    )->None:
        super().__init__(
            name="Brawl",
            description="Brawl is a measure of how well you can fight in close-combat.",
            proficiency=proficiency,
        )

class Lockpick(Skill):

    def __init__(
            self,
            proficiency: ProficiencyNames = ProficiencyNames.UNTRAINED,
    )->None:
        super().__init__(
            name="Lockpick",
            description="Lockpick is a measure of how well you can pick locks.",
            proficiency=proficiency,
        )

class Medicine(Skill):

    def __init__(
            self,
            proficiency: ProficiencyNames = ProficiencyNames.UNTRAINED,
    )->None:
        super().__init__(
            name="Medicine",
            description="Medicine is a measure of how well you can heal wounds.",
            proficiency=proficiency,
        )

class Mechanics(Skill):

    def __init__(
            self,
            proficiency: ProficiencyNames = ProficiencyNames.UNTRAINED,
    )->None:
        super().__init__(
            name="Mechanics",
            description="Mechanics is a measure of how well you can repair machines.",
            proficiency=proficiency,
        )

class Computers(Skill):

    def __init__(
            self,
            proficiency: ProficiencyNames = ProficiencyNames.UNTRAINED,
    )->None:
        super().__init__(
            name="Computers",
            description="Computers is a measure of how well you can hack computers.",
            proficiency=proficiency,
        )

class Driving(Skill):

    def __init__(
            self,
            proficiency: ProficiencyNames = ProficiencyNames.UNTRAINED,
    )->None:
        super().__init__(
            name="Driving",
            description="Driving is a measure of how well you can drive vehicles.",
            proficiency=proficiency,
        )

class Stealth(Skill):

    def __init__(
            self,
            proficiency: ProficiencyNames = ProficiencyNames.UNTRAINED,
    )->None:
        super().__init__(
            name="Stealth",
            description="Stealth is a measure of how well you can hide.",
            proficiency=proficiency,
        )

class Perception(Skill):

    def __init__(
            self,
            proficiency: ProficiencyNames = ProficiencyNames.UNTRAINED,
    )->None:
        super().__init__(
            name="Perception",
            description="Perception is a measure of how well you can notice things.",
            proficiency=proficiency,
        )

class SkillMap(Enum):
    DEXTERITY = Dexterity
    AIM = Aim
    ATHLETICS = Athletics
    BRAWL = Brawl
    LOCKPICK = Lockpick
    MEDICINE = Medicine
    MECHANICS = Mechanics
    COMPUTERS = Computers
    DRIVING = Driving
    STEALTH = Stealth
    PERCEPTION = Perception