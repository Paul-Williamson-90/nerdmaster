from src.triggers.base import Trigger, TriggerResponse
from src.environments.base import Environment

from typing import List

class EnvironmentTrigger(Trigger):
    pass

class TriggerDialogue(EnvironmentTrigger):
    """
    Trigger's an NPC to begin dialogue with the player.
    """

    def __init__(
            self,
            npc_names: List[str] = [],
            narrative_prompt: str = "",
            req_quest_ids: List[str] = [],
            exl_quest_ids: List[str] = [],
    ):
        self.attributes = {}
        self.attributes["characters"] = npc_names
        self.attributes["narrative_prompt"] = narrative_prompt
        self.attributes["req_quest_ids"] = req_quest_ids
        self.attributes["exl_quest_ids"] = exl_quest_ids
    
    def prepare(
            self,
            environment: Environment,
            req_quest_ids: List[str]=[], # Quests that need to be completed before this dialogue can be triggered
            exl_quest_ids: List[str]=[], # Quests that can't be active/already triggered for this dialogue to trigger
    ):
        characters = [character.name for character in environment.character_locations]
        # if atleast one character is present in the location
        if not any([character in characters for character in self.attributes["characters"]]):
            return 
        # if all the required quests are completed
        if not all([quest_id in req_quest_ids for quest_id in self.attributes["req_quest_ids"]]):
            return
        # if no exclusive quests are active
        if any([quest_id in exl_quest_ids for quest_id in self.attributes["exl_quest_ids"]]):
            return
        return self

    def activate(
            self,
    ):
        """
        Game logic for activating the trigger
        Triggers a dialogue from the NPC.
        Triggers are resolved by the Game class, post NPC agent output.
        """
        return TriggerResponse(
            narrative_message=self.attributes["narrative_prompt"],
            # triggers=[AddCharacterToTurns(character) for character in self.attributes["characters"]]
        )