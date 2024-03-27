from typing import List

from src.characters.prompts import BACKGROUND_STR

class Background:

    def __init__(
            self,
            backstory: str,
            personality: str,
            views_beliefs: str,
            factions: List[str|None] = [],
    )->None:
        self.backstory = backstory
        self.personality = personality
        self.views_beliefs = views_beliefs
        self.factions = factions

    def __str__(
            self,
    )->str:
        return BACKGROUND_STR.format(
            backstory=self.backstory,
            personality=self.personality,
            views_beliefs=self.views_beliefs,
            factions=self.factions,
        )
    
    def get_backstory(
            self,
    )->str:
        return self.backstory
    
    def get_personality(
            self,
    )->str:
        return self.personality
    
    def get_views_beliefs(
            self,
    )->str:
        return self.views_beliefs
    
    def get_factions(
            self,
    )->List[str|None]:
        return self.factions
    
    def add_to_backstory(
            self,
            addition: str,
    )->str:
        self.backstory += addition
    
    def add_to_personality(
            self,
            addition: str,
    )->str:
        self.personality += addition
    
    def add_to_views_beliefs(
            self,
            addition: str,
    )->str:
        self.views_beliefs += addition
    
    def add_to_factions(
            self,
            addition: str,
    )->List[str|None]:
        self.factions.append(addition)
    
    def remove_from_factions(
            self,
            removal: str,
    )->List[str|None]:
        if removal in self.factions:
            self.factions.remove(removal)
    