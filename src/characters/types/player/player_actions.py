from src.characters.actions.base import ReActionMap
from src.game.terms import GameMode
from src.triggers.base import Trigger
from src.characters.base import Character
from src.triggers.player_triggers import (
    Speak, 
    SearchMemory, 
    StageDirection, 
    Attack,
    PrepareAttack,
    LeaveConversation,
    LookAround
)

from typing import Dict

class PlayerReActionMap(ReActionMap):

    def __init__(
            self,
            character: Character,
    ):
        self.character: Character = character
        self.action_map: Dict[str, Dict[str, Trigger]] = {
            GameMode.DIALOGUE.value: {
                "speak": Speak(character=character).prepare,
                "search_memory": SearchMemory(character=character).prepare,
                "stage_direction": StageDirection(character=character).prepare,
                "prepare_attack": PrepareAttack(character=character).prepare,
                "leave_conversation": LeaveConversation(character=character).prepare,
                # "look_at_character": None, # TODO: Implement this
                # "look_around": None, # TODO: Implement this
            },
            GameMode.COMBAT.value: {
                "attack": Attack(character=character).prepare,
                "stage_direction": StageDirection(character=character).prepare,
                # "take_cover": None, # TODO: Implement this
                # "surrender": None, # TODO: Implement this
                # "run_away": None, # TODO: Implement this
                # "scream_for_help": None, # TODO: Implement this
            },
            GameMode.EXPLORE.value: {
                "search_memory": SearchMemory(character=character).prepare,
                "stage_direction": StageDirection(character=character).prepare,
                # "look_at_character": None, # TODO: Implement this
                "look_around": LookAround(character=character).prepare,
            }
        }

    def get_reaction(
            self,
            event: str,
            mode: str,
    ):
        tools = self._get_tools(mode)
        self.character.agent.update_tools(tools)
        final_output = self.character.agent.get_reaction(event, self.character.name)
        return final_output

