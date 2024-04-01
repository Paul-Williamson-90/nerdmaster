from src.game.terms import NarrationType, Turn, GameMode
from src.triggers.base import Trigger, TriggerResponse
from src.characters.base import Character
from src.utils.combat import combat
from src.utils.prepare_attack import prepare_attack_action

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

        game.next_turn = Turn.GAME.value

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
            game.game_mode = GameMode.EXPLORE.value
        
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