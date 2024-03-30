from typing import Dict
from src.triggers.base import Trigger, TriggerResponse
from src.characters.base import Character
from src.game.terms import Turn
from src.utils.combat import combat
from src.utils.prepare_attack import prepare_attack_action



class NPCAction(Trigger):

    def __init__(
            self,
            character: Character,
            attributes: Dict[str, str] = {}
    ):
        super().__init__(trigger_id=self.__class__.__name__)
        self.character: Character = character
        self.attributes: Dict[str, str] = attributes


class SearchMemory(NPCAction):

    def prepare(
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
        self.attributes["query"] = query
        return self.activate()

    def activate(
            self,
    ):
        response = self.character.memory.search_memory(self.attributes["query"], self.character.name)
        return response

class Speak(NPCAction):

    def prepare(
            self,
            dialogue: str,
    ):
        """
        <desc>Respond to a narrative event with a dialogue from your character. Ensure you remain in-character and only output the words the character is speaking, no stage directions should be added.</desc>

        Args
        str - <dialogue>: The dialogue your character is responding with.
        """
        self.attributes = {
            "dialogue": dialogue,
        }
        self.character.add_to_action_queue(self)
        return f"**Tool Action Accepted**: You will say '{dialogue}' at the end of your turn."

    def activate(
            self,
            game,
    ):
        dialogue = self.attributes["dialogue"]

        game.add_to_npc_narrator(
            text=dialogue,
            characters=[char.name for char in game.characters],
            text_tag=self.character.name,
            ai_generate=True,
        )
        
        game.add_character_dialogue_to_narrator(
            text=dialogue,
            character=self.character,
        )

        return TriggerResponse(
            log_message=f"Activated {self.trigger_id}: {self.character.name} says: {dialogue}",
        )
    


class Attack(NPCAction):
    """
    NPC Action for attacking a character
    """

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
            "attacking": self.character.name,
            "defending": character_to_attack,
        }
        self.character.add_to_action_queue(self)
        return f"Tool Action Accepted: You will attack {character_to_attack} at the end of your turn."

    def activate(
            self,
            game
    ):
        """
        Game logic for activating the trigger
        Character and target_character are entered by Game using retrieved attributes and matching.
        """
        attacking = game.player
        defending = [char for char in game.characters if char.name == self.attributes["defending"]][0]
        
        assert defending, f"Character {self.attributes['defending']} not found in game characters."
        
        game.next_turn = Turn.PLAYER.value
        
        return combat(
            game=game,
            trigger_id=self.trigger_id,
            attacking=attacking,
            defending=defending,
        )


class PrepareAttack(NPCAction):
    """
    NPC Action for preparing to attack a character, initiative roll for who goes first / if the character has a chance to respond
    """
    def prepare(self,
                character_to_attack: str,
    )->str:
        """
        <desc>Prepare to attack a character. You should only choose this if it suits your character's narrative in response to the event.</desc>
        """
        self.attributes = {
            "attacking_character": self.character.name,
            "target_character": character_to_attack,
        }
        self.character.add_to_action_queue(self)
        return f"**Tool Action Accepted**: You will prepare to attack {character_to_attack} at the end of your turn."

    def activate(
            self,
            game,
    ):
        defending = game.get_in_focus_character(self.attributes["target_character"])
        attacking = game.get_in_focus_character(self.attributes["attacking_character"])

        return prepare_attack_action(game=game, 
            trigger_id=self.trigger_id, 
            attacking=attacking, 
            defending=defending, 
            attack_action=Attack
        )

