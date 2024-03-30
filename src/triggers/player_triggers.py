from src.game.game import Game, GameMode, Turn, NarrationType
from src.triggers.base import Trigger, TriggerResponse
from src.characters.types.player.player import Player
from src.utils.combat import combat
from src.utils.prepare_attack import prepare_attack_action

from abc import ABC, abstractmethod


class PlayerAction(Trigger, ABC):
    
        def __init__(
                self,
                trigger_id: str,
                character: Player,
                attributes: dict = {},
        ):
            super().__init__(trigger_id=trigger_id)
            self.attributes = attributes
            self.character: Player = character
            
    
        @abstractmethod
        def prepare(
                self,
        ):
            ...

        @abstractmethod
        def activate(
                self,
                game: Game
        ):
            ...

class StageDirection(PlayerAction):

    def prepare(
            self,
            stage_direction: str,
    ):
        """
        <desc>Write a third-person stage direction that describes how the player's character is emoting. This must only contain physical descriptions without dialogue. You can use this tool to compliment other tools/actions chosen.</desc>

        Args
        str - <stage_direction>: The stage direction for the player's character.
        """
        self.attributes["stage_direction"] = stage_direction
        self.character.add_to_action_queue(self)
        return f"Stage direction prepared: {stage_direction}"

    def activate(
            self,
            game: Game
    ):
        game.add_to_player_narrator(
            text=self.attributes["stage_direction"],
            text_tag=NarrationType.stage.value,
            ai_generate=False,
        )

        game.add_to_npc_narrator(
            text=self.attributes["stage_direction"],
            text_tag=NarrationType.stage.value,
            characters=[char.name for char in game.characters],
            ai_generate=False,
        )

        game.next_turn = Turn.GAME.value

        return TriggerResponse(log_message=f"Trigger {self.trigger_id} activated.")

class Speak(PlayerAction):

    def prepare(
            self,
            dialogue: str,
    ):
        """
        <desc>Make the player's character speak</desc>

        Args
        str - <dialogue>: The dialogue the player's character will say.
        """
        self.attributes["dialogue"] = dialogue
        self.character.add_to_action_queue(self)
        return f"Dialogue prepared: {dialogue}"

    def activate(
            self,
            game: Game
    ):
        player_name = game.player.name
        dialogue = self.attributes["dialogue"]
        characters = [char.name for char in game.characters]

        if len(characters) == 0:
            game.add_to_player_narrator(
                text = f"{player_name} randomly starts talking to themself... Perhaps they are going mad.",
                ai_generate=True,
            )
            return TriggerResponse(
                log_message=f"Trigger {self.trigger_id} activated. No characters to speak to.",)
        
        game.add_to_player_narrator(
            text=self.attributes["stage_direction"],
            text_tag=self.character.name,
            ai_generate=False,
            voice=self.character.voice,
        )

        game.add_to_npc_narrator(
            text=dialogue,
            text_tag=player_name,
            characters=characters,
            ai_generate=False,
        )

        game.next_turn = Turn.GAME.value
        game.switch_game_mode(GameMode.DIALOGUE.value)

        return TriggerResponse(log_message=f"Trigger {self.trigger_id} activated.")
        

class SearchMemory(PlayerAction):

    def prepare(
            self,
            query: str,
    ):
        """
        Game logic for activating the trigger
        Triggers a search in the NPC's memory.
        This happens in-agent.

        <desc>Search the player's character's memory using a question. For example, "Do I remember anything regarding..."</desc>

        Args
        str - <query>: The query/thought/question to search your own character's memory with.
        """
        self.attributes["query"] = query
        self.character.add_to_action_queue(self)
        return f"Memory search prepared: {query}"

    def activate(
            self,
            game: Game
    ):
        response = game.player.search_memory(self.attributes["query"])

        game.add_to_player_narrator(
            text=response,
            text_tag=NarrationType.stage.value,
            ai_generate=False,
            voice=self.character.voice,
        )

        return TriggerResponse(log_message=f"Trigger {self.trigger_id} activated.")

class Attack(PlayerAction):
    """
    Player action for attacking a character
    """
    def prepare(
            self,
            character_to_attack: str,
    )->str:
        """
        <desc>Make the player's character attempt to attack another character</desc>

        Args
        str - <character_to_attack>: The name of the character the player's character will attack.
        """
        self.attributes = {
            "attacking": self.character.name,
            "defending": character_to_attack,
        }
        self.character.add_to_action_queue(self)
        return f"Attack prepared: {self.character.name} will attack {character_to_attack} at the end of the turn."

    def activate(
            self,
            game: Game
    ):
        """
        Game logic for activating the trigger
        Character and target_character are entered by Game using retrieved attributes and matching.
        """
        attacking = game.player
        defending = [char for char in game.characters if char.name == self.attributes["defending"]][0]
        
        assert defending, f"Character {self.attributes['defending']} not found in game characters."
        
        game.next_turn = Turn.GAME.value
        
        return combat(
            game=game,
            trigger_id=self.trigger_id,
            attacking=attacking,
            defending=defending,
        )


class PrepareAttack(PlayerAction):
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
            game: Game,
    ):
        defending = game.get_in_focus_character(self.attributes["target_character"])
        attacking = game.get_in_focus_character(self.attributes["attacking_character"])

        return prepare_attack_action(game=game, 
            trigger_id=self.trigger_id, 
            attacking=attacking, 
            defending=defending, 
            attack_action=Attack
        )

