from typing import Dict
from src.triggers.base import Trigger, TriggerResponse, Dialogue
from src.characters.base import Character
from src.characters.types.npcs.npc_actions import NPCReActionMap
from src.utils.rolls import normal_roll
from src.configs import DifficultyConfigs




class NPCAction(Trigger):

    def __init__(
            self,
            trigger_id: str,
            npc_action_object: NPCReActionMap,
            attributes: Dict[str, str] = {},
    ):
        super().__init__(trigger_id=trigger_id, attributes=attributes)
        self.npc_action_object = npc_action_object


class SearchMemory(NPCAction):

    trigger_map = {}

    def prepare(
            self,
            search_term: str,
    ):
        pass

    def activate(
            self,
            query: str,
    ):
        """
        Game logic for activating the trigger
        Triggers a search in the NPC's memory.
        This happens in-agent.

        <desc>Search your own character's memory using a question. For example, "Do I remember anything regarding..."</desc>

        Args
        str - <query>: The query/thought/question to search your own character's memory with.
        """
        character = self.npc_action_object.character
        response = character.memory.search_memory(query, character.name)
        return response

class Speak(NPCAction):

    trigger_map = {}

    def prepare(
            self,
            dialogue: str,
    ):
        """
        <desc>Respond to a narrative event with a dialogue</desc>

        Args
        str - <dialogue>: The dialogue your character is responding with.
        """
        self.attributes = {
            "dialogue": dialogue,
        }
        self.npc_action_object.add_trigger(self)
        return f"**Tool Action Accepted**: You will say '{dialogue}' at the end of your turn."

    def activate(
            self,
            dialogue: str,
    ):
        """
        Game logic for activating the trigger
        Triggers a dialogue from the NPC.
        Triggers are resolved by the Game class, post NPC agent output.
        """
        character = self.npc_action_object.character
        return TriggerResponse(
            narrative_message=dialogue,
            triggers = Dialogue().prepare(character=character, dialogue=dialogue)
        )
    


class Attack(NPCAction):
    """
    NPC Action for attacking a character
    """
    trigger_map = {}

    def prepare(
            self,
            character_to_attack: str,
    )->str:
        """
        <desc>Choose to attack a character. You should only choose this if it suits your character's narrative in response to the event.</desc>

        Args
        str - <character_to_attack>: The name of the character you will attack attack
        """
        self.attributes = {
            "attacking": self.npc_action_object.character.name,
            "defending": character_to_attack,
        }
        self.npc_action_object.add_trigger(self)
        return f"**Tool Action Accepted**: You will attack {character_to_attack} at the end of your turn."

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
        skill, weapon_name, weapon_modifier = attacking.equipped_items.get_weapon_attack_stats()
        attack_disadvantage = attacking.health.get_roll_modifier()
        attack = attacking.skills.get_modifier(skill) + weapon_modifier - attack_disadvantage

        defense = defending.skills.get_modifier("DEXTERITY") + (1 if defending_coverage else 0)
        defense += defending.health.get_roll_modifier()

        dc = DifficultyConfigs.ATTACK_DC.value

        if normal_roll(dc, attack-defense):
            narrative_message = f"{attacking.name} attacks {defending.name} with their {weapon_name} and hits!\n"
            narrative_message += defending.health.take_damage(narrative_message) # TODO: Implement this on health
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
                character_to_attack: str,
    )->str:
        """
        <desc>Prepare to attack a character. You should only choose this if it suits your character's narrative in response to the event.</desc>
        """
        self.attributes = {
            "attacking_character": self.npc_action_object.character.name,
            "target_character": character_to_attack,
        }
        self.npc_action_object.add_trigger(self)
        return f"**Tool Action Accepted**: You will prepare to attack {character_to_attack} at the end of your turn."

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

