from src.game.configs import GameDataPaths
from src.environments.environment_loaders import (
    EnvironmentLoader, 
)
from src.environments.base import Environment
from src.items.item_loader import ItemLoader
from src.characters.types.npcs.load_npc import NPCLoader
from src.characters.types.player.player import Player
from src.triggers.base import Trigger
from src.characters.types.npcs.npc import NPC
from src.endpoints.gpt import StandardGPT
from src.game.prompts import PLAYER_NARRATION_SYSTEM_MESSAGE
from src.voices.voice import Voice

from typing import List, Dict

from enum import Enum
from dataclasses import dataclass

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

@dataclass
class Narration:

    def __init__(
            self,
            text: str|None,
            audio_path: str|None,
            image_path: str|None,
    ):
        self.text = text
        self.audio_path = audio_path
        self.image_path = image_path

    def to_dict(self):
        return {
            "text": self.text,
            "audio_path": self.audio_path,
            "image_path": self.image_path,
        }

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
    ):  
        # loaders
        self.environment_loader: EnvironmentLoader = environment_loader
        self.item_loader: ItemLoader = item_loader
        self.npc_loader: NPCLoader = npc_loader
        # in game data
        self.data_paths: GameDataPaths = data_paths
        self.player: Player = player
        self.environment: Environment = environment
        self.game_mode: str = GameMode.EXPLORE.value
        self.characters: List[NPC] = []
        self.model: StandardGPT = model(model=model_name)
        self.narrator: Voice = narrator(
            voice="echo",
        )
        self.narration_queue: Dict[int, Narration] = {}
        self.next_turn: str = Turn.GAME.value

    def save_game(self):
        # TODO: Implement save game
        pass

    def fetch_triggers_environment(self):
        quest_log = self.player.quest_log
        armed_triggers = self.environment.fetch_active_triggers(
            quest_log = quest_log
        )
        return armed_triggers
    
    def add_to_characters(
            self,
            characters: List[str],
    ):
        for character in characters:
            loaded_character = self.npc_loader.load_character(character)
            self.characters.append(loaded_character)

    def remove_from_characters(
            self,
            characters: List[str]|str,
    ):
        if isinstance(characters, str):
            characters = [characters]
        for character in characters:
            self.characters = [c for c in self.characters if c.name != character]

    def add_to_npc_narrator(
            self,
            text: str|Dict[str, str],
            text_tag: str, # stage or character name
            characters: List[str],
            ai_generate: bool = False,
    ):
        # TODO: Tidy this up!
        if isinstance(text, str):
            if ai_generate:
                if text_tag == "stage":
                    system_message = PLAYER_NARRATION_SYSTEM_MESSAGE
                    response = self.model.generate(prompt=text, system_message=system_message)
                else:
                    response = text
            else:
                response = text
            text = f"<{text_tag}>{response}</{text_tag}>"
            for character in self.characters:
                character.add_to_narration_queue(text)

        else:
            for character, text in characters.items():
                character = [character for character in self.characters if character.name == character][0]
                if ai_generate:
                    if text_tag == "stage":
                        system_message = PLAYER_NARRATION_SYSTEM_MESSAGE
                        response = self.model.generate(prompt=text, system_message=system_message)
                    else:
                        response = text
                else:
                    response = text
                response = f"<{text_tag}>{response}</{text_tag}>"
                character.add_to_narration_queue(response)

    def switch_game_mode(
            self,
            mode: GameMode,
    ):
        self.game_mode = GameMode(mode).value
    
    def add_to_narrator(
            self,
            text: str,
            ai_generate: bool = False,
    ):  
        if ai_generate:
            text = self.model.generate(prompt=text, system_message=PLAYER_NARRATION_SYSTEM_MESSAGE)
        audio_path = self.narrator.generate(text)
        self.narration_queue[len(self.narration_queue)] = Narration(
            text = text,
            audio_path = audio_path,
            # image_path = image_path
        )
    
    def activate_trigger(
            self, 
            trigger:Trigger
    ):
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

    def game_environment_turn(
            self,
    ):
        self.next_turn = Turn.PLAYER.value
        # fetch triggers
        prepared_triggers = self.fetch_triggers_environment()
        # reconcile prepared triggers
        self._reconcile_triggers(prepared_triggers) 
        # increment turns in location
        self.environment.add_turn()

    
    def character_reaction_turn(
            self,
    ):
        if len(self.characters)==1:
            self.characters[0].character_reaction(
                event = "insert dialogue/narrative here", # TODO: Implement dialogue system
                name = self.player.name, # TODO: Check character knows player name
                mode = self.game_mode, # TODO: Ensure all are using same mode Enum
                chat_history=self.player.chat_history, # TODO: Fix this
            )
        else:
            raise NotImplementedError("Character reaction for multiple not implemented yet.")

    def game_turn(
            self,
    ):
        if self.game_mode == GameMode.EXPLORE.value:
            self.game_environment_turn()
        elif self.game_mode == GameMode.DIALOGUE.value or self.game_mode == GameMode.COMBAT.value:
            self.character_reaction_turn()
        else:
            raise ValueError(f"Game mode {self.game_mode} not recognized")
        
    def load_new_map(
            self,
    ):
        raise NotImplementedError("NEW_MAP mode not implemented")
        
    def start_turn(
            self,
    ):
        if self.next_turn == Turn.PLAYER.value:
            # TODO: Implement player turn separately as it requires an input from FE
            return # self.activate_player_actions() these are stored 
        elif self.next_turn == Turn.GAME.value:
            # This will trigger naturally after player turn if game turn is set as so
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
        
        payload = self.narration_queue
        self.narration_queue = {}
        # this will be sent to the FE to play the audio and display the text/images
        return {k:n.to_dict() for k, n in payload.items()} 
        
        

        



