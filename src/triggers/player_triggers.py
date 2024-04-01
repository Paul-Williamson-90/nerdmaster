from src.game.terms import NarrationType, Turn, GameMode
from src.triggers.base import Trigger, TriggerResponse
from src.characters.base import Character
from src.utils.combat import combat
from src.utils.prepare_attack import prepare_attack_action

from typing import Dict

from abc import ABC, abstractmethod


class PlayerAction(Trigger, ABC):
    
        def __init__(
                self,
                character: Character,
                attributes: dict = {},
        ):
            super().__init__(trigger_id=self.__class__.__name__)
            self.attributes = attributes
            self.character: Character = character
            
        # @print_func_name
        @abstractmethod
        def prepare(
                self,
        ):
            ...

        # @print_func_name
        @abstractmethod
        def activate(
                self,
                game
        ):
            ...

class LookAround(PlayerAction):

    def prepare(
            self,
    ):
        """
        <desc>Make the player's character look around the environment</desc>
        """
        self.character.add_to_action_queue(self)
        return "**Tool Action Accepted**"
    
    def activate(
            self,
            game
    ):
        game.add_to_player_narrator(
            text=f"You look around at the environment around you, looking for things of interest...",
            text_tag=NarrationType.stage.value,
            ai_generate=False,
        )

        # game.environment.fetch_triggers_explore()
        game.environment.arm_reveal_triggers(game.player.quest_log)

        game.switch_turn(Turn.GAME.value) # Do not remove, it means that the game checks any triggers after explore mode

        return TriggerResponse(
            log_path=game.data_paths.logs_path,
            log_message=f"Trigger {self.trigger_id} activated."
        )

class StageDirection(PlayerAction):

    # @print_func_name
    def prepare(
            self,
            stage_direction: str,
    ):
        """
        <desc>Write a third-person stage direction that describes how the player's character is emoting. This must only contain physical descriptions without dialogue. You can use this tool to compliment other tools/actions chosen.</desc>

        Args
        str - <stage_direction>: The stage direction for the player's character.
        """
        # print(self.__class__.__name__, "prepare")
        self.attributes["stage_direction"] = stage_direction
        self.character.add_to_action_queue(self)
        return "**Tool Action Accepted**"

    # @print_func_name
    def activate(
            self,
            game
    ):
        # print(self.__class__.__name__, "activate")
        game.add_to_player_narrator(
            text=self.attributes["stage_direction"],
            text_tag=NarrationType.stage.value,
            ai_generate=False,
        )

        game.add_to_npc_narrator(
            text=self.attributes["stage_direction"],
            text_tag=NarrationType.stage.value,
            ai_generate=False,
        )

        game.switch_turn(Turn.GAME.value)

        return TriggerResponse(
            log_path=game.data_paths.logs_path,
            log_message=f"Trigger {self.trigger_id} activated."
        )
    
class LeaveConversation(PlayerAction):

    # @print_func_name
    def prepare(
            self,
    ):
        """
        <desc>Make the player's character leave the conversation</desc>
        """
        # print(self.__class__.__name__, "prepare")
        self.character.add_to_action_queue(self)
        return "**Tool Action Accepted**"
    
    # @print_func_name
    def activate(
            self,
            game
    ):
        # print(self.__class__.__name__, "activate")
        # TODO: Check characters for any no-leave triggers/flags

        game.add_to_player_narrator(
            text=f"{self.character.name} leaves the conversation.",
            text_tag=NarrationType.stage.value,
            ai_generate=True,
        )

        game.add_to_npc_narrator(
            text=f"{self.character.name} leaves the conversation.",
            text_tag=NarrationType.stage.value,
            ai_generate=True,
        )

        game.remove_from_characters()

        game.switch_game_mode(GameMode.EXPLORE.value)
        game.switch_turn(Turn.PLAYER.value)

        return TriggerResponse(
            log_path=game.data_paths.logs_path,
            log_message=f"Trigger {self.trigger_id} activated."
        )

class Speak(PlayerAction):

    # @print_func_name
    def prepare(
            self,
            dialogue: str,
    ):
        """
        <desc>Make the player's character speak</desc>

        Args
        str - <dialogue>: The dialogue the player's character will say.
        """
        # print(self.__class__.__name__, "prepare")
        self.attributes["dialogue"] = dialogue
        self.character.add_to_action_queue(self)
        return "**Tool Action Accepted**"

    # @print_func_name
    def activate(
            self,
            game
    ):
        # print(self.__class__.__name__, "activate")
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
            text=f"\"{self.attributes["dialogue"]}\"",
            text_tag=self.character.name,
            ai_generate=False,
            voice=self.character.voice,
        )

        game.add_to_npc_narrator(
            text=dialogue,
            text_tag=player_name,
            ai_generate=False,
        )

        game.switch_turn(Turn.GAME.value)
        game.switch_game_mode(GameMode.DIALOGUE.value)

        return TriggerResponse(
            log_path=game.data_paths.logs_path,
            log_message=f"Trigger {self.trigger_id} activated."
        )
        

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
            game
    ):
        response = game.player.search_memory(self.attributes["query"])

        game.add_to_player_narrator(
            text=response,
            text_tag=NarrationType.stage.value,
            ai_generate=False,
            voice=self.character.voice,
        )

        return TriggerResponse(
            log_path=self.character.game.data_paths.logs_path,
            log_message=f"Activated {self.trigger_id}: {self.character.name} searches memory for {self.attributes['query']}",
        )

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
        return "**Tool Action Accepted**"

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
        
        game.switch_turn(Turn.GAME.value)
        
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
        return "**Tool Action Accepted**"

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
    
class LookAtCharacter(PlayerAction):

    def prepare(
            self,
            character_to_look_at: str,
    ):
        """
        <desc>Make the player's character look at another character, getting a visual description of the character of interest.</desc>

        Args
        str - <character_to_look_at>: The name of the character the player's character will look at.
        """
        self.attributes = {
            "target_character": character_to_look_at,
        }
        self.character.add_to_action_queue(self)
        return "**Tool Action Accepted**"

    def activate(
            self,
            game
    ):

        target_character = game.get_in_focus_character(self.attributes["target_character"])

        game.add_to_player_narrator(
            text=f"You take a deep look at the person in front of you.",
            text_tag=NarrationType.stage.value,
            ai_generate=False,
        )

        game.add_to_player_narrator(
            text=target_character.get_visual_description(),
            text_tag=NarrationType.stage.value,
            ai_generate=False,
        )

        return TriggerResponse(
            log_path=game.data_paths.logs_path,
            log_message=f"Trigger {self.trigger_id} activated."
        )
    
class LookDeeper(PlayerAction):
    """
    Deeper interaction with observed object.
    """
    def prepare(
            self,
    ):
        """
        <desc>Make the player's character look around the environment</desc>
        """
        self.character.add_to_action_queue(self)
        return "**Tool Action Accepted**"
    
    def activate(
            self,
            game
    ):
        object_of_interest = game.environment.get_object_of_interest()

        name = object_of_interest.name
        items = object_of_interest.reveal_items_and_triggers(game.player.quest_log)

        game.add_to_player_narrator(
            text=f"You take a deeper look at the {name}.",
            text_tag=NarrationType.stage.value,
            ai_generate=False,
        )

        if len(items)==0:
            game.add_to_player_narrator(
                text=f"You find nothing of interest.",
                text_tag=NarrationType.stage.value,
                ai_generate=False,
            )
            game.switch_game_mode(GameMode.EXPLORE.value)
        
        elif len(items)>0:
            game.add_to_player_narrator(
                text=f"You notice the following items: {', '.join([x.name for x in items])}",
                text_tag=NarrationType.stage.value,
                ai_generate=False,
            )
            game.switch_game_mode(GameMode.TRADE.value)
            # TODO: Trigger item management screen
            # TODO: On exit, revert to Explore mode

        return TriggerResponse(
            log_path=game.data_paths.logs_path,
            log_message=f"Trigger {self.trigger_id} activated."
        )
    
class GetRevealedAttributes(PlayerAction):

    def prepare(
            self,
    ):
        """
        <desc>Get details on what objects and characters the player can interact with. This should be used to get the information to correctly select objects for player interactions.</desc>
        """
        # TODO: How do we get game/environment?
        revealed: Dict[str, str] = self.character.game.environment.get_revealed()
        revealed_str = ""
        for obj in revealed:
            revealed_str += f"Name: {obj['name']}\nDescription: {obj['description']}\nObject Type: {obj["type"]}\n\n"
        return revealed_str
    
    def activate(
            self,
            game
    ):
        pass

class BeginDialogue(PlayerAction):

    def prepare(
            self,
            characters_to_speak_to: str,
    ):
        """
        <desc>Make the player's character begin a dialogue with other character(s)</desc>

        Args
        str - <characters_to_speak_to>: The **name** of the characters the player's character will approach to speak to.
        """
        # Validate if choice is valid
        valid = False
        acceptable_choices = self.character.game.environment.get_revealed()
        acceptable_choices = [x for x in acceptable_choices if x["type"]=="CharacterPosition"]

        for choice in acceptable_choices:
            if choice["name"] == characters_to_speak_to:
                valid = True
                break

        if valid:
            self.attributes = {
                "character_position": characters_to_speak_to,
            }
            self.character.add_to_action_queue(self)
            return "**Tool Action Accepted**"
        
        else:
            message = "**Tool Action Rejected**: Invalid character choice."
            for choice in acceptable_choices:
                message += f"Name: {choice['name']}\nDescription: {choice['description']}\nObject Type: {choice["type"]}\n\n"
            return message

    def activate(
            self,
            game
    ):

        characters = [x for x in game.environment.character_locations 
         if x.name == self.attributes["character_position"] and x.hidden is False][0].characters

        game.add_to_characters(
            characters=characters,
        )

        game.add_to_player_narrator(
                text=f"You approach, ready for conversation. What will you say?",
                text_tag=NarrationType.stage.value,
                ai_generate=False,
        )

        game.switch_turn(Turn.PLAYER.value)
        game.switch_game_mode(GameMode.DIALOGUE.value)

        return TriggerResponse(
            log_path=game.data_paths.logs_path,
            log_message=f"Trigger {self.trigger_id} activated."
        )