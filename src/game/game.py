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
from src.game.terms import GameMode, Turn, NarrationType
from src.characters.types.player.load_player import PlayerLoader

from typing import List, Dict
# from src.utils.tools import print_func_name
    
    
class GameEnvironmentTurn:

    def __init__(
            self,
            game: "Game",
    ):
        self.game = game

    # @print_func_name
    def fetch_triggers_environment(self):
        """
        These triggers are provided on game environment turn.
        """
        quest_log = self.game.player.quest_log
        armed_triggers = self.game.environment.fetch_active_triggers(
            quest_log = quest_log
        )
        return armed_triggers
    
    def fetch_triggers_explore(self):
        """
        These triggers are provided when the player chooses to explore the environment.
        """
        quest_log = self.game.player.quest_log
        prepared_triggers = self.game.environment.fetch_reveal_triggers(
            quest_log = quest_log
        )
        self.game.action_queue += prepared_triggers
    
    # @print_func_name
    def game_environment_turn(
            self,
    ):
        # fetch triggers
        prepared_triggers = self.fetch_triggers_environment()
        # reconcile prepared triggers
        self.game._reconcile_triggers(prepared_triggers) 
        # increment turns in location
        self.game.add_turn()
        self.game.action_queue = []
        self.game.environment.armed_triggers = []


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
            game_mode: GameMode = GameMode.EXPLORE.value,
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
        self.game_mode: GameMode = game_mode
        self.characters: List[NPC] = []
        self.model: StandardGPT = model(model=model_name)
        self.narrator: Voice = narrator(voice="echo")
        self.narrator_collector: Narrator = narrator_collector()
        self.environment_turn: GameEnvironmentTurn = environment_turn(self)
        self.next_turn: Turn = Turn.GAME.value
        self.action_queue: List[Trigger] = []

    # @print_func_name
    def add_character_actions_to_queue(
            self,
            character: Character
    ):
        self.action_queue += character.get_action_queue()

    # @print_func_name
    def save_game(self):
        """
        Triggers the save game process (only during exploration mode)
        """
        data = self.player.save()
        loader = PlayerLoader()
        loader.save_player(data)

        self.narrator_collector.add_narration(
            text="Game saved.",
        )
        # TODO: Save game state

    # @print_func_name
    def add_turn(
            self,
    ):
        """
        Increment the turn tickers for environment and any conditions on characters.
        """
        # TODO: Character tickers
        self.environment.add_turn()
    
    # @print_func_name
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

    # @print_func_name
    def remove_from_characters(
            self,
    ):
        """
        Removes NPC characters from game focus.

        Args:
        characters (List[str]|str): List of character names to remove from game focus.
        """
        characters = self.characters
        for character in characters:
            save_json = character.save() # TODO: Consider keeping short-term and removing it if leave environment
            self.npc_loader.character_save(character.name, save_json)
        self.characters = []

    # @print_func_name
    def _ai_generate_narration(
            self,
            text: str,
    ):
        """
        Rewrite narration text using AI.
        """
        system_message = PLAYER_NARRATION_SYSTEM_MESSAGE
        response = self.model.generate(prompt=text, system_prompt=system_message)
        return response
    
    # @print_func_name
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

    # @print_func_name
    def _add_to_npc_narrator_multiple(
            self,
            text: Dict[str, str],
            text_tag: str,
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

    # @print_func_name
    def add_to_npc_narrator(
            self,
            text: str|Dict[str, str],
            text_tag: str, # stage or character name
            ai_generate: bool = False,
    ):
        if isinstance(text, str):
            self._add_to_npc_narrator_single(text, text_tag, ai_generate)
        else:
            self._add_to_npc_narrator_multiple(text, text_tag, ai_generate)

    # @print_func_name
    def switch_game_mode(
            self,
            mode: GameMode,
    ):
        self.game_mode = GameMode(mode).value
    
    # @print_func_name
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
                system_prompt=PLAYER_NARRATION_SYSTEM_MESSAGE
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

    # @print_func_name
    def add_character_dialogue_to_narrator(
            self,
            text: str,
            character: Character,
    ):
        if text[0] != "\"":
            text = "\""+text
        if text[-1] != "\"":
            text = text+"\""

        text = f"<{character.name}>{text}</{character.name}>"
        
        audio_path = character.voice.generate(text)
        self.narrator_collector.add_narration(
            text=text, 
            audio_path=audio_path,
            # image_path=image_path,
        )

    # @print_func_name
    def get_in_focus_character(
            self,
            name: str,
    ):
        for character in self.characters:
            if character.name == name:
                return character
        return None
    
    # @print_func_name
    def activate_trigger(
            self, 
            trigger:Trigger,
    ):
        out = trigger.activate(self)
        return out
    
    # @print_func_name
    def _prepare_triggers(
            self,
            triggers: List[Trigger],
    ):
        # Fetching
        if triggers:
            triggers = [self.trigger_loader.get_trigger(x) if isinstance(x, str) 
                            else x for x in triggers]
            # Preparing
            prepared_triggers = []
            for trigger in triggers:
                if trigger.trigger_type == "environment":
                    trigger.prepare(
                        environment=self.environment,
                        quest_log=self.player.quest_log
                    )
                    prepared_triggers.append(trigger)
                elif trigger.trigger_type == "character":
                    trigger.prepare()
                    prepared_triggers.append(trigger)
            return prepared_triggers
        return []
    
    # @print_func_name
    def _reconcile_triggers(
            self,
            triggers: List[Trigger],
    ):
        if not triggers:
            return
        if len(triggers) == 0:
            return 
        elif len(triggers) == 1:
            trigger_response = self.activate_trigger(triggers[0])
            triggers = trigger_response.triggers
            triggers = self._prepare_triggers(triggers)
            self._reconcile_triggers(triggers)
        else:
            new_triggers = []
            for trigger in triggers:
                trigger_response = self.activate_trigger(trigger)
                trig_adds = trigger_response.triggers
                trig_adds = self._prepare_triggers(trig_adds)
                new_triggers.extend(trig_adds)
            self._reconcile_triggers(new_triggers)

    # @print_func_name
    def reconcile_all_characters(
            self,
    ):
        for character in self.characters:
            self.add_character_actions_to_queue(character)
        self.add_character_actions_to_queue(self.player)
        self._reconcile_triggers(self.action_queue)
        self.action_queue = []
    
    # @print_func_name
    def NPC_reaction_turn(
            self,
    ):
        if len(self.characters)==1:
            character: NPC = self.characters[0]
            character.character_reaction(
                mode = self.game_mode, 
            )
        else:
            raise NotImplementedError("Character reaction for multiple not implemented yet.")

        self.reconcile_all_characters()

    # @print_func_name
    def game_turn(
            self,
    ):
        if self.game_mode not in [GameMode.EXPLORE.value, GameMode.DIALOGUE.value, GameMode.COMBAT.value]:
            raise ValueError(f"Game mode {self.game_mode} not recognized")
        
        if self.game_mode == GameMode.EXPLORE.value and self.next_turn == Turn.GAME.value:
            self.environment_turn.game_environment_turn()
            print("Post-env",self.action_queue)
        
        if (self.game_mode in [GameMode.DIALOGUE.value, GameMode.COMBAT.value]
            and self.next_turn == Turn.GAME.value):
            self.NPC_reaction_turn()
            print("Post-npc",self.action_queue)
    
    # @print_func_name
    def load_new_map(
            self,
    ):
        raise NotImplementedError("NEW_MAP mode not implemented")
    
    # @print_func_name
    def activate_player_actions(
            self,
    ):
        self.add_character_actions_to_queue(self.player)
        self._reconcile_triggers(self.action_queue)
        self.action_queue = []

    # @print_func_name 
    def turn_order(
            self,
    ):
        if self.next_turn == Turn.PLAYER.value:
            self.activate_player_actions()
            # self._reconcile_triggers(self.action_queue) 
            # self.action_queue = []
        if self.next_turn == Turn.GAME.value:
            self.game_turn()
            print("Post Game",self.action_queue)
        elif self.next_turn == Turn.SAVE.value:
            self.save_game()
        elif self.next_turn == Turn.NEW_MAP.value:
            self.load_new_map()
        elif self.next_turn == Turn.QUIT.value:
            self.save_game()
            return
        else:
            raise ValueError(f"Turn {self.next_turn} not recognized")
        self.next_turn = Turn.PLAYER.value
        
    # @print_func_name
    def get_player_reaction(
            self,
            event: str
    ):
        self.player.reactions.get_reaction(event, self.game_mode)
        
    # @print_func_name
    def player_turn(
            self,
            player_input: str,
    ):
        self.get_player_reaction(player_input)
    
    # @print_func_name
    def play(
            self,
            player_input: str|None = None,
    ):
        if self.next_turn == Turn.PLAYER.value:
            if player_input is None:
                raise ValueError("Player input required for player turn")
            self.player_turn(player_input)

        self.turn_order()
        return self.narrator_collector.get_narration_queue()
        
        
    
        
        
        
        
        

