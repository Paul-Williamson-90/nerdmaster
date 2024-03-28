from src.triggers.base import TriggerResponse, Trigger
from src.characters.base import Character
from src.utils.rolls import normal_roll
from src.configs import DifficultyConfigs

from typing import Dict, List
    
"""
NPCActionMap:
- Controls what actions are available to an NPC at a given time.
- Collects any triggers as a result of an action being taken.
- Triggers are resolved by the Game class, post NPC agent output.

NPCAction(Trigger):
- Abstract class for NPC actions.
- Contains a reference to the NPCActionMap object for adding triggers.
- Inherits from Trigger class.
"""

class NPCActionMap:

    collected_triggers: List[Trigger] = []

    def __init__(
            self,
            character: Character,
    ):
        self.character = character # needed for accessing character's connected modules
        self.action_map: Dict[str, Dict[str, Trigger]] = {
            "dialogue": {
                "prepare_attack": PrepareAttack(npc_action_object=self).prepare,
                "react_to_character": None, # TODO: Implement this
            },
            "combat": {
                "attack": Attack(npc_action_object=self).prepare,
                "take_cover": None, # TODO: Implement this
                "surrender": None, # TODO: Implement this
                "run_away": None, # TODO: Implement this
                "scream_for_help": None, # TODO: Implement this
            }
        }

    def add_trigger(self, trigger: Trigger):
        self.collected_triggers.append(trigger)

    def get_triggered_triggers(self):
        collected_triggers = self.collected_triggers
        self.collected_triggers = []
        return collected_triggers

class NPCAction(Trigger):
    npc_action_object: NPCActionMap


class Attack(NPCAction):
    """
    NPC Action for attacking a character
    """
    trigger_map = {}
    def prepare(
            self,
            attacking: str,
            defending: str,
    ):
        self.attributes = {
            "attacking": attacking,
            "defending": defending,
        }
        self.npc_action_object.add_trigger(self)

    def activate(
            self,
            attacking: Character,
            defending: Character,
            defending_coverage: bool = False,
    ):
        """
        Game logic for activating the trigger
        Character and target_character are entered by Game using retrieved attributes and matching.
        """
        skill = attacking.equipped_items.get_weapon_skill_type() # TODO: Implement this on equipped items
        weapon_name = attacking.equipped_items.get_weapon_name() # TODO: Implement this on equipped items
        weapon_modifier = attacking.skills.get_modifier(skill)
        attack = weapon_modifier + attacking.equipped_items.get_attack_bonus() # TODO: Implement this on equipped items

        defense = defending.skills.get_modifier("DEXTERITY") + (1 if defending_coverage else 0)

        dc = DifficultyConfigs.ATTACK_DC.value

        if normal_roll(dc, attack-defense):
            narrative_message = f"{attacking.name} attacks {defending.name} with their {weapon_name} and hits!\n"
            narrative_message += defending.health.take_damage() # TODO: Implement this on health
            return TriggerResponse(
                narrative_message=narrative_message,
            )
        else:
            narrative_message = f"{attacking.name} attacks {defending.name} with their {weapon_name} and misses!"
            return TriggerResponse(
                narrative_message=narrative_message,
            )



class PrepareAttack(NPCAction):
    """
    NPC Action for preparing to attack a character, initiative roll for who goes first / if the character has a chance to respond
    """
    trigger_map = {
        "Attack": Attack,
    }

    def prepare(self,
                attacking_character: str,
                target_character: str,
    ):
        self.attributes = {
            "attacking_character": attacking_character,
            "target_character": target_character,
        }
        self.npc_action_object.add_trigger(self)

    def activate(
            self,
            character: Character,
            target_character: Character,
    ):
        """
        Game logic for activating the trigger
        Character and target_character are entered by Game using retrieved attributes and matching.
        """
        character_dex_mod = character.skills.get_modifier("DEXTERITY")
        target_character_dex_mod = target_character.skills.get_modifier("DEXTERITY")
        target_character_perc_mod = target_character.skills.get_modifier("PERCEPTION")
        target_mod = max([target_character_dex_mod, target_character_perc_mod])
        dc = DifficultyConfigs.PREPARE_ATTACK_DC.value

        if normal_roll(dc, character_dex_mod-target_mod):
            prepared_trigger = self.trigger_map["Attack"]()
            narrative_message = f"{character.name} attacks {target_character.name}, {target_character.name} is caught off guard!"
            prepared_trigger.prepare(attacking=character.name, defending=target_character.name)
            return TriggerResponse(
                triggers=prepared_trigger,
                narrative_message=narrative_message,
            )

        else:
            narrative_message = f"{target_character.name} notices {character.name} is about to attack!"
            return TriggerResponse(
                triggers=None,
                narrative_message=narrative_message,
            )

