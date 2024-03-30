from src.characters.actions.base import ReActionMap
from src.triggers.base import Trigger
from src.characters.base import Character
from src.triggers.npc_triggers import PrepareAttack, SearchMemory, Speak, Attack
from src.game.terms import GameMode

from typing import Dict
    

class NPCReActionMap(ReActionMap):

    def __init__(
            self,
            character: Character,
      ):
        self.character: Character = character # needed for accessing character's connected modules
        self.action_map: Dict[str, Dict[str, Trigger]] = {
            GameMode.DIALOGUE.value: {
                "prepare_attack": PrepareAttack(character=character).prepare,
                "search_memory": SearchMemory(character=character).prepare,
                "speak": Speak(character=character).prepare,
                # "look_at_character": None, # TODO: Implement this
                # "look_around": None, # TODO: Implement this
            },
            GameMode.COMBAT.value: {
                "attack": Attack(character=character).prepare,
                # "take_cover": None, # TODO: Implement this
                # "surrender": None, # TODO: Implement this
                # "run_away": None, # TODO: Implement this
                # "scream_for_help": None, # TODO: Implement this
            }
        }

    def get_reaction(
            self,
            event: str,
            mode: str,
            additional_tools: dict = {},
    ):
        tools = self._get_tools(mode)
        tools.update(additional_tools)
        self.character.agent.update_tools(tools)
        final_output = self.character.agent.get_reaction(event, self.character.background, self.character.name)
        return final_output
    
    
