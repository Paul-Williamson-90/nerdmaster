from src.game.configs import GameDataPaths
from src.environments.environment_loaders import (
    EnvironmentLoader, 
)
from src.environments.base import Environment
from src.items.item_loader import ItemLoader
from src.characters.types.npcs.load_npc import NPCLoader
from src.characters.types.player.player import Player
from src.triggers.base import Trigger
from src.triggers.trigger_loaders import TriggerLoader
from src.characters.types.npcs.npc import NPC
from src.characters.base import Character
from src.endpoints.gpt import StandardGPT
from src.game.prompts import PLAYER_NARRATION_SYSTEM_MESSAGE
from src.voices.voice import Voice
from src.narrator.narrator import Narrator

from typing import List, Dict

from enum import Enum

class GameMode(Enum):

    EXPLORE = "explore"
    INTERACT = "interact"
    TRADE = "trade"
    DIALOGUE = "dialogue"
    COMBAT = "combat"

class Turn(Enum):
    
    PLAYER = "player"
    GAME = "game"
    SAVE = "save"
    NEW_MAP = "new_map"
    QUIT = "quit"

class NarrationType(Enum):

    stage = "stage"
    dialogue = "dialogue"



    
    
class GameEnvironmentTurn:

    def __init__(
            self,
            game: "Game",
    ):
        self.game = game

    def fetch_triggers_environment(self):
        quest_log = self.game.player.quest_log
        armed_triggers = self.game.environment.fetch_active_triggers(
            quest_log = quest_log
        )
        return armed_triggers
    
    def game_environment_turn(
            self,
    ):
        # fetch triggers
        prepared_triggers = self.fetch_triggers_environment()
        # reconcile prepared triggers
        self.game._reconcile_triggers(prepared_triggers) 
        # increment turns in location
        self.game.add_turn()
        self.next_turn = Turn.PLAYER.value


class Game:

    def __init__(
            self,
            # in game data
            player: Player,
            environment: Environment,
            data_paths: GameDataPaths,
            # loaders
            environment_loader: EnvironmentLoader,
            item_loader: ItemLoader,
            npc_loader: NPCLoader,
            model: StandardGPT = StandardGPT,
            model_name: str = "gpt-3.5-turbo",
            narrator: Voice = Voice,
            environment_turn: GameEnvironmentTurn = GameEnvironmentTurn,
            trigger_loader: TriggerLoader = TriggerLoader,
            narrator_collector: Narrator = Narrator,
    ):  
        # loaders
        self.environment_loader: EnvironmentLoader = environment_loader
        self.item_loader: ItemLoader = item_loader
        self.npc_loader: NPCLoader = npc_loader
        self.trigger_loader: TriggerLoader = trigger_loader
        # in game data
        self.data_paths: GameDataPaths = data_paths
        self.player: Player = player
        self.environment: Environment = environment
        self.game_mode: str = GameMode.EXPLORE.value
        self.characters: List[NPC] = []
        self.model: StandardGPT = model(model=model_name)
        self.narrator: Voice = narrator(voice="echo")
        self.narrator_collector: Narrator = narrator_collector
        self.environment_turn: GameEnvironmentTurn = environment_turn(self)
        self.next_turn: str = Turn.GAME.value
        self.action_queue: List[Trigger] = []

    def add_character_actions_to_queue(
            self,
            character: Character
    ):
        self.action_queue += character.get_action_queue()

    def save_game(self):
        """
        Triggers the save game process (only during exploration mode)
        """
        self.narrator_collector.add_narration(
            text="Game saved.",
        )
        # TODO: Save game state

    def add_turn(
            self,
    ):
        """
        Increment the turn tickers for environment and any conditions on characters.
        """
        # TODO: Character tickers
        self.environment.add_turn()
    
    def add_to_characters(
            self,
            characters: List[str],
    ):
        """
        Loads NPC characters into game focus.

        Args:
        characters (List[str]): List of character names to load into game focus.
        """
        for character in characters:
            loaded_character = self.npc_loader.load_character(character)
            self.characters.append(loaded_character)

    def remove_from_characters(
            self,
            characters: List[str]|str,
    ):
        """
        Removes NPC characters from game focus.

        Args:
        characters (List[str]|str): List of character names to remove from game focus.
        """
        if isinstance(characters, str):
            characters = [characters]
        for character in characters:
            self.characters = [c for c in self.characters if c.name != character]

    def _ai_generate_narration(
            self,
            text: str,
    ):
        """
        Rewrite narration text using AI.
        """
        system_message = PLAYER_NARRATION_SYSTEM_MESSAGE
        response = self.model.generate(prompt=text, system_message=system_message)
        return response
    
    def _add_to_npc_narrator_single(
            self,
            text: str,
            text_tag: str,
            ai_generate: bool,
    ):
        """
        Adds text to NPC stage/dialogue queue (input is used for character reactions)
        """
        # TODO: Consider the character perception of the event via system prompt injection
        if ai_generate and text_tag == NarrationType.stage.value:
            response = self._ai_generate_narration(text)
        else:
            response = text
        text = f"<{text_tag}>{response}</{text_tag}>"
        for character in self.characters:
            character.add_short_term_memory(text)

    def _add_to_npc_narrator_multiple(
            self,
            text: Dict[str, str],
            text_tag: str,
            characters: List[NPC],
            ai_generate: bool,
    ):
        """
        Adds text to NPC stage/dialogue queue (input is used for character reactions)
        Used for multiple characters, each with their own perception of the event.
        """
        # TODO: Consider the character perception of the event via system prompt injection
        for character, text in text.items():
            character = [character for character in self.characters if character.name == character][0]
            if ai_generate and text_tag == NarrationType.stage.value:
                response = self._ai_generate_narration(text)
            else:
                response = text
            text = f"<{text_tag}>{response}</{text_tag}>"
            character.add_short_term_memory(text)

    def add_to_npc_narrator(
            self,
            text: str|Dict[str, str],
            text_tag: str, # stage or character name
            characters: List[str],
            ai_generate: bool = False,
    ):
        if isinstance(text, str):
            self._add_to_npc_narrator_single(text, text_tag, characters, ai_generate)
        else:
            self._add_to_npc_narrator_multiple(text, text_tag, characters, ai_generate)

    def switch_game_mode(
            self,
            mode: GameMode,
    ):
        self.game_mode = GameMode(mode).value
    
    def add_to_player_narrator(
            self,
            text: str,
            text_tag: str = NarrationType.stage.value,
            voice: Voice = None,
            ai_generate: bool = False,
    ):  
        if ai_generate:
            text = self.model.generate(
                prompt=text, 
                system_message=PLAYER_NARRATION_SYSTEM_MESSAGE
            )

        voice = voice if voice else self.narrator
        audio_path = voice.generate(text)

        text = f"<{text_tag}>{text}</{text_tag}>"

        self.narrator_collector.add_narration(
            text=text, 
            audio_path=audio_path,
            # image_path=image_path,
        )
        self.player.add_short_term_memory(text)

    def add_character_dialogue_to_narrator(
            self,
            text: str,
            character: Character,
    ):
        audio_path = character.voice.generate(text)
        self.narrator_collector.add_narration(
            text=text, 
            audio_path=audio_path,
            # image_path=image_path,
        )

    def get_in_focus_character(
            self,
            name: str,
    ):
        for character in self.characters:
            if character.name == name:
                return character
        return None
    
    def activate_trigger(
            self, 
            trigger:Trigger|str,
    ):
        if isinstance(trigger, str):
            trigger = self.trigger_loader.get_trigger(trigger)
        out = trigger.activate(self)
        return out
        
    def _reconcile_triggers(
            self,
            triggers: List[Trigger],
    ):
        if len(triggers) == 0:
            return 
        elif len(triggers) == 1:
            trigger_response = self.activate_trigger(triggers[0])
            triggers = trigger_response.triggers
            self._reconcile_triggers(triggers)
        else:
            new_triggers = []
            for trigger in triggers:
                trigger_response = self.activate_trigger(trigger)
                new_triggers.extend(trigger_response.triggers)
            self._reconcile_triggers(new_triggers)

    
    def NPC_reaction_turn(
            self,
    ):
        if len(self.characters)==1:
            character: NPC = self.characters[0]
            character.character_reaction(
                event = character.get_short_term_memory(),
                name = self.player.name, # TODO: Check character knows player name
                mode = self.game_mode, # TODO: Ensure all are using same mode Enum
            )
        else:
            raise NotImplementedError("Character reaction for multiple not implemented yet.")

    def game_turn(
            self,
    ):
        if self.game_mode == GameMode.EXPLORE.value and self.next_turn == Turn.GAME.value:
            self.environment_turn.game_environment_turn()
        
        if (self.game_mode in [GameMode.DIALOGUE.value, GameMode.COMBAT.value]
            and self.next_turn == Turn.GAME.value):
            self.NPC_reaction_turn()

        if self.game_mode not in GameMode.__members__.values():
            raise ValueError(f"Game mode {self.game_mode} not recognized")
        
    def load_new_map(
            self,
    ):
        raise NotImplementedError("NEW_MAP mode not implemented")
    
    def activate_player_actions(
            self,
    ):
        self.add_character_actions_to_queue(self.player)
        self._reconcile_triggers(self.action_queue)
        
    def turn_order(
            self,
    ):
        if self.next_turn == Turn.PLAYER.value:
            self.activate_player_actions()
        elif self.next_turn == Turn.GAME.value:
            self.game_turn()
        elif self.next_turn == Turn.SAVE.value:
            self.save_game()
        elif self.next_turn == Turn.NEW_MAP.value:
            self.load_new_map()
        elif self.next_turn == Turn.QUIT.value:
            self.save_game()
            return
        else:
            raise ValueError(f"Turn {self.next_turn} not recognized")
        
    def get_player_reaction(
            self,
            event: str
    ):
        return self.player.reactions.get_reaction(event, self.game_mode)
        
    def player_turn(
            self,
            player_input: str,
    ):
        _ = self.get_player_reaction(player_input)
        self.turn_order()
        return self.narrator_collector.get_narration_queue()
        
        
    
        
        
        
        
        

