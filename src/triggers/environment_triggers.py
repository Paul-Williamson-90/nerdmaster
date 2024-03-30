from src.triggers.base import Trigger, TriggerResponse
from src.quests.base import QuestLog
from src.environments.base import Environment
from src.game.terms import NarrationType
from abc import ABC, abstractmethod

from typing import List, Dict
import numpy as np

class EnvironmentTrigger(Trigger, ABC):

    trigger_type = "environment"

    def __init__(
            self,
            trigger_id: str,
            ids_to_trigger: List[str],
            narrative_prompt: str|None = None,
            random_chance: float = 1.0,
            req_active_quest_ids: List[str] = [], # Quests that need to be active for trigger
            req_quest_completed_ids: List[str] = [], # Quests that need to be completed for trigger
            exl_quest_active_ids: List[str] = [], # Quests that can't be active for trigger
            exl_quest_completed_ids: List[str] = [], # Quests that can't be completed for trigger
            req_trigger_ids: List[str] = [], # Triggers that need to have been active for trigger
            exl_trigger_ids: List[str] = [], # Triggers that can't have been active for trigger
            req_characters: List[str] = [], # Characters that need to be present in the location
            attributes: Dict[str, str] = {},
    ):
        super().__init__(trigger_id)
        self.narrative_prompt = narrative_prompt
        self.req_active_quest_ids = req_active_quest_ids
        self.req_quest_completed_ids = req_quest_completed_ids
        self.exl_quest_active_ids = exl_quest_active_ids
        self.exl_quest_completed_ids = exl_quest_completed_ids
        self.req_trigger_ids = req_trigger_ids
        self.exl_trigger_ids = exl_trigger_ids
        self.ids_to_trigger = ids_to_trigger
        self.req_characters = req_characters
        self.random_chance = random_chance
        self.attributes: Dict[str, str] = attributes
    
    def prepare(
            self,
            quest_log: QuestLog,
            environment: Environment,
    )->Trigger|None:
        
        active_quest_ids = quest_log.active_quest_ids
        completed_quest_ids = quest_log.completed_quest_ids
        completed_trigger_ids = quest_log.completed_trigger_ids

        self.validate(
            environment=environment,
            active_quest_ids=active_quest_ids,
            completed_quest_ids=completed_quest_ids,
            completed_trigger_ids=completed_trigger_ids,
        )
        
    @abstractmethod
    def validate(
            self,
            environment: Environment,
            active_quest_ids: List[str]=[], # Quests that need to be completed before this can be triggered
            completed_quest_ids: List[str]=[], # Quests that can't be active/already triggered for this to trigger
            completed_trigger_ids: List[str]=[], # Triggers that can't be already triggered for this to trigger
    ):
        ...

    def activate(
            self,
            game
    ):
        """
        Game logic for activating the trigger
        Triggers a dialogue from the NPC.
        Triggers are resolved by the Game class, post NPC agent output.
        """
        return TriggerResponse(
            triggers=self.ids_to_trigger,
            narrative_message=self.narrative_prompt,
            attributes = self.attributes,
            log_message=f"Trigger {self.trigger_id} activated."
        )

    def val_turns_in_location(
            self,
            environment: Environment,
            n_turns: int,
            sign: str,
    ):
        """
        Validate the number of turns the player has been in the location
        """
        if sign == ">":
            return environment.turns_in_location > n_turns
        elif sign == "<":
            return environment.turns_in_location < n_turns
        elif sign == "==":
            return environment.turns_in_location == n_turns
        elif sign == ">=":
            return environment.turns_in_location >= n_turns
        elif sign == "<=":
            return environment.turns_in_location <= n_turns
        elif sign == "!=":
            return environment.turns_in_location != n_turns
        else:
            raise ValueError(f"Invalid sign: {sign}")
        
    def val_req_quests_completed(
            self,
            completed_quest_ids: List[str]
    ):
        """
        Validate all required quests are completed
        """
        return all([quest_id in completed_quest_ids for quest_id in self.req_quest_completed_ids])
    
    def val_req_active_quests(
            self,
            active_quest_ids: List[str],
    ):
        """
        Validate all required quests are active
        """
        return all([quest_id in active_quest_ids for quest_id in self.req_active_quest_ids])
    
    def val_quests_not_active(
            self,
            active_quest_ids: List[str],
    ):
        """
        Validate certain quests are not active
        """
        return not any([quest_id in active_quest_ids for quest_id in self.exl_quest_active_ids])
    
    def val_triggers_not_prev_active(
            self,
            completed_trigger_ids: List[str],
    ):
        """
        Validate certain triggers are not active
        """
        return not any([trigger_id in completed_trigger_ids for trigger_id in self.exl_trigger_ids])
    
    def val_random_chance_trigger(
            self,
    ):
        """
        Validate if the trigger should be triggered by random chance
        """
        return np.random.choice([True, False], p=[self.random_chance, 1-self.random_chance])
    
    def val_quest_log_requirements(
            self,
            active_quest_ids: List[str],
            completed_quest_ids: List[str],
            completed_trigger_ids: List[str],
    ):
        """
        Validate the quest log requirements for the trigger
        """
        if not self.val_req_active_quests(active_quest_ids):
            # print(f"Failed req active quests: {self.req_active_quest_ids}")
            return False
        if not self.val_req_quests_completed(completed_quest_ids):
            # print(f"Failed req completed quests: {self.req_quest_completed_ids}")
            return False
        if not self.val_quests_not_active(active_quest_ids):
            # print(f"Failed exl active quests: {self.exl_quest_active_ids}")
            return False
        if not self.val_triggers_not_prev_active(completed_trigger_ids):
            # print(f"Failed exl active triggers: {self.exl_trigger_ids}")
            return False
        return True
    
    def val_any_req_characters_present(
            self,
            environment: Environment,
    ):
        """
        Validate if the characters are present in the location
        """
        characters = [character.name  for character_locations in environment.character_locations 
                      for character in character_locations.characters]
        return any([character in characters for character in self.req_characters])
    
    def val_all_req_characters_present(
            self,
            environment: Environment,
    ):
        """
        Validate if all characters are present in the location
        """
        characters = [character for character_locations in environment.character_locations 
                      for character in character_locations.characters]
        return all([character in characters for character in self.req_characters])
    
    def get_characters_present_names(
            self,
            environment: Environment,
    ):  
        """
        Get the names of the characters present in the location that are connected to the trigger
        """
        characters = [character for character_locations in environment.character_locations 
                      for character in character_locations.characters]
        return [name for name in characters if name in self.req_characters]
    
class DescribeLocationTrigger(EnvironmentTrigger):
    """
    Trigger the narrator to give a visual description of the location.
    """

    def validate(
            self,
            environment: Environment,
            active_quest_ids: List[str]=[], # Quests that need to be completed before this can be triggered
            completed_quest_ids: List[str]=[], # Quests that can't be active/already triggered for this to trigger
            completed_trigger_ids: List[str]=[], # Triggers that can't be active/already triggered for this to trigger
    ):
        if not self.val_quest_log_requirements(active_quest_ids, completed_quest_ids, completed_trigger_ids):
            return
        
        self.attributes["location_description"] = environment.get_visual_description()
        environment.arm_trigger(self)

    def activate(
            self,
            game
    ):
        print(self.attributes)
        game.add_to_player_narrator(
            text=self.attributes["location_description"],
            text_tag=NarrationType.stage.value,
            ai_generate=False,
        )

        return TriggerResponse(
            triggers=self.ids_to_trigger,
            log_message=f"Trigger {self.trigger_id} activated."
        )

class TurnsInLocationTrigger(EnvironmentTrigger):
    """
    Trigger another trigger after a certain number of turns in the location
    """
    def __init__(
            self,
            trigger_id: str,
            ids_to_trigger: List[str],
            narrative_prompt: str|None = None,
            random_chance: float = 1.0,
            req_active_quest_ids: List[str] = [], # Quests that need to be active for trigger
            req_quest_completed_ids: List[str] = [], # Quests that need to be completed for trigger
            exl_quest_active_ids: List[str] = [], # Quests that can't be active for trigger
            exl_quest_completed_ids: List[str] = [], # Quests that can't be completed for trigger
            req_trigger_ids: List[str] = [], # Triggers that need to have been active for trigger
            exl_trigger_ids: List[str] = [], # Triggers that can't have been active for trigger
            req_characters: List[str] = [], # Characters that need to be present in the location
            turns_in_location: int = 0,
            sign: str = "==",
    ):
        super().__init__(
            trigger_id=trigger_id,
            ids_to_trigger=ids_to_trigger,
            narrative_prompt=narrative_prompt,
            random_chance=random_chance,
            req_active_quest_ids=req_active_quest_ids,
            req_quest_completed_ids=req_quest_completed_ids,
            exl_quest_active_ids=exl_quest_active_ids,
            exl_quest_completed_ids=exl_quest_completed_ids,
            req_trigger_ids=req_trigger_ids,
            exl_trigger_ids=exl_trigger_ids,
            req_characters=req_characters,
        )
        self.turns_in_location = turns_in_location
        self.sign = sign

    def validate(
            self,
            environment: Environment,
            active_quest_ids: List[str]=[], # Quests that need to be completed before this can be triggered
            completed_quest_ids: List[str]=[], # Quests that can't be active/already triggered for this to trigger
            completed_trigger_ids: List[str]=[], # Triggers that can't be active/already triggered for this to trigger
    ):
        if not self.val_quest_log_requirements(active_quest_ids, completed_quest_ids, completed_trigger_ids):
            return
        if not self.val_turns_in_location(environment, self.turns_in_location, self.sign):
            return
        if not self.val_random_chance_trigger():
            return 
        environment.arm_trigger(self)
        
    
class OnExitTrigger(EnvironmentTrigger):
    """
    DO NOT ATTACH ON ENVIRONMENT MAIN TRIGGERS LIST
    TODO: Attach triggers to local/connecting locations functionality
    """

    def validate(
            self,
            environment: Environment,
            active_quest_ids: List[str]=[], # Quests that need to be completed before this can be triggered
            completed_quest_ids: List[str]=[], # Quests that can't be active/already triggered for this to trigger
            completed_trigger_ids: List[str]=[], # Triggers that can't be active/already triggered for this to trigger
    ):
        if not self.val_quest_log_requirements(active_quest_ids, completed_quest_ids, completed_trigger_ids):
            return
        # TODO: Implement exit checker

        if not self.val_random_chance_trigger():
            return 
        environment.arm_trigger(self)


class OnEntryTrigger(EnvironmentTrigger):        
    """
    Trigger another trigger on player entry to a location
    """
    def validate(
            self,
            environment: Environment,
            active_quest_ids: List[str]=[], # Quests that need to be completed before this can be triggered
            completed_quest_ids: List[str]=[], # Quests that can't be active/already triggered for this to trigger
            completed_trigger_ids: List[str]=[], # Triggers that can't be active/already triggered for this to trigger
    ):
        if not self.val_quest_log_requirements(active_quest_ids, completed_quest_ids, completed_trigger_ids):
            return
        if not self.val_turns_in_location(environment, 0, "=="):
            return
        if not self.val_random_chance_trigger():
            return 
        environment.arm_trigger(self)
        

class TriggerEventAnyCharacter(EnvironmentTrigger):
    """
    Trigger's another trigger when one of the characters specified are present.
    """
    def __init__(
            self,
            trigger_id: str,
            event_type: str,
            ids_to_trigger: List[str],
            narrative_prompt: str|None = None,
            narrative_prompt_player: str|None = None,
            narrative_prompt_npc: str|Dict[str,str]|None = None,
            random_chance: float = 1.0,
            req_active_quest_ids: List[str] = [], # Quests that need to be active for trigger
            req_quest_completed_ids: List[str] = [], # Quests that need to be completed for trigger
            exl_quest_active_ids: List[str] = [], # Quests that can't be active for trigger
            exl_quest_completed_ids: List[str] = [], # Quests that can't be completed for trigger
            req_trigger_ids: List[str] = [], # Triggers that need to have been active for trigger
            exl_trigger_ids: List[str] = [], # Triggers that can't have been active for trigger
            req_characters: List[str] = [], # Characters that need to be present in the location
    ):
        super().__init__(
            trigger_id=trigger_id,
            ids_to_trigger=ids_to_trigger,
            narrative_prompt=narrative_prompt,
            random_chance=random_chance,
            req_active_quest_ids=req_active_quest_ids,
            req_quest_completed_ids=req_quest_completed_ids,
            exl_quest_active_ids=exl_quest_active_ids,
            exl_quest_completed_ids=exl_quest_completed_ids,
            req_trigger_ids=req_trigger_ids,
            exl_trigger_ids=exl_trigger_ids,
            req_characters=req_characters,
        )
        self.narrative_prompt_player = narrative_prompt_player
        self.narrative_prompt_npc = narrative_prompt_npc
        self.event_type = event_type
        
    
    def validate(
            self,
            environment: Environment,
            active_quest_ids: List[str]=[], # Quests that need to be completed before this dialogue can be triggered
            completed_quest_ids: List[str]=[], # Quests that can't be active/already triggered for this dialogue to trigger
            completed_trigger_ids: List[str]=[], # Triggers that can't be active/already triggered for this to trigger
    ):
        if not self.val_any_req_characters_present(environment):
            return
        if not self.val_quest_log_requirements(active_quest_ids, completed_quest_ids, completed_trigger_ids):
            return
        if not self.val_random_chance_trigger():
            return 
        self.attributes["characters"] = self.get_characters_present_names(environment)
        self.attributes["narrative_prompt_player"] = self.narrative_prompt_player
        self.attributes["narrative_prompt_npc"] = self.narrative_prompt_npc
        environment.arm_trigger(self)

    def activate(
            self,
            game
    ):  
        
        game.add_to_player_narrator(
            text=self.narrative_prompt_player,
            text_tag=NarrationType.stage.value,
            ai_generate=True,
        )
        
        game.add_to_characters(
            characters=self.attributes["characters"],
        )
        game.add_to_npc_narrator(
            text=self.narrative_prompt_npc, 
            text_tag=NarrationType.stage.value,
            characters=self.attributes["characters"],
            ai_generate=True
        )
        game.switch_game_mode(self.event_type)

        return TriggerResponse(log_message=f"Trigger {self.trigger_id} activated.")
    
class TriggerEventAllCharacter(EnvironmentTrigger):
    """
    Trigger's another trigger when all of the characters specified are present.
    """

    def __init__(
            self,
            trigger_id: str,
            event_type: str,
            ids_to_trigger: List[str],
            narrative_prompt: str|None = None,
            narrative_prompt_player: str|None = None,
            narrative_prompt_npc: str|Dict[str, str]|None = None,
            random_chance: float = 1.0,
            req_active_quest_ids: List[str] = [], # Quests that need to be active for trigger
            req_quest_completed_ids: List[str] = [], # Quests that need to be completed for trigger
            exl_quest_active_ids: List[str] = [], # Quests that can't be active for trigger
            exl_quest_completed_ids: List[str] = [], # Quests that can't be completed for trigger
            req_trigger_ids: List[str] = [], # Triggers that need to have been active for trigger
            exl_trigger_ids: List[str] = [], # Triggers that can't have been active for trigger
            req_characters: List[str] = [], # Characters that need to be present in the location
    ):
        super().__init__(
            trigger_id=trigger_id,
            ids_to_trigger=ids_to_trigger,
            narrative_prompt=narrative_prompt,
            random_chance=random_chance,
            req_active_quest_ids=req_active_quest_ids,
            req_quest_completed_ids=req_quest_completed_ids,
            exl_quest_active_ids=exl_quest_active_ids,
            exl_quest_completed_ids=exl_quest_completed_ids,
            req_trigger_ids=req_trigger_ids,
            exl_trigger_ids=exl_trigger_ids,
            req_characters=req_characters,
        )
        self.narrative_prompt_player = narrative_prompt_player
        self.narrative_prompt_npc = narrative_prompt_npc
        self.event_type = event_type

    def validate(
            self,
            environment: Environment,
            active_quest_ids: List[str]=[], # Quests that need to be completed before this dialogue can be triggered
            completed_quest_ids: List[str]=[], # Quests that can't be active/already triggered for this dialogue to trigger
            completed_trigger_ids: List[str]=[], # Triggers that can't be active/already triggered for this to trigger
    ):
        if not self.val_all_req_characters_present(environment):
            return
        if not self.val_quest_log_requirements(active_quest_ids, completed_quest_ids, completed_trigger_ids):
            return
        if not self.val_random_chance_trigger():
            return 
        self.attributes["characters"] = self.get_characters_present_names(environment)
        self.attributes["narrative_prompt_player"] = self.narrative_prompt_player
        self.attributes["narrative_prompt_npc"] = self.narrative_prompt_npc
        environment.arm_trigger(self)

    def activate(
            self,
            game
    ):
        game.add_to_player_narrator(
            text=self.narrative_prompt_player, 
            text_tag=NarrationType.stage.value, 
            ai_generate=True
        )
        game.add_to_characters(
            characters=self.attributes["characters"],
        )
        game.add_to_npc_narrator(
            text=self.narrative_prompt_npc, 
            text_tag=NarrationType.stage.value,
            characters=self.attributes["characters"],
            ai_generate=True
        )
        game.switch_game_mode(self.event_type)

        return TriggerResponse(log_message=f"Trigger {self.trigger_id} activated.")