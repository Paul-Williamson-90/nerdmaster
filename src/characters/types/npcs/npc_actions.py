from src.triggers.base import Trigger
from src.characters.base import Character
from src.characters.types.prompts import NPC_PERCEPTION_SYSTEM_PROMPT, PERCEPTION_FORMAT
from src.triggers.npc_triggers import PrepareAttack, SearchMemory, Speak, Attack
from src.gpt import StandardGPT

from typing import Dict, List
from src.utils.tools import create_npc_action_tool
    
"""
NPCActionMap:
- Controls what actions are available to an NPC at a given time.
- Collects any triggers as a result of an action being taken.
- Triggers are resolved by the Game class, post NPC agent output.

NPCAction(Trigger):
- Abstract class for NPC actions.
- Contains a reference to the NPCActionMap object for adding triggers.
- Inherits from Trigger class.
"""



class NPCReActionMap:

    collected_triggers: List[Trigger] = []

    def __init__(
            self,
            character: Character,
            model: StandardGPT = StandardGPT,
            model_name: str = "gpt-3.5-turbo",
    ):
        self.model = self._prepare_model(model, model_name)
        self.character = character # needed for accessing character's connected modules
        self.action_map: Dict[str, Dict[str, Trigger]] = {
            "dialogue": {
                "prepare_attack": PrepareAttack(npc_action_object=self).prepare,
                "search_memory": SearchMemory(npc_action_object=self).activate,
                "speak": Speak(npc_action_object=self).prepare,
                # "look_at_character": None, # TODO: Implement this
                # "look_around": None, # TODO: Implement this
            },
            "combat": {
                "attack": Attack(npc_action_object=self).prepare,
                # "take_cover": None, # TODO: Implement this
                # "surrender": None, # TODO: Implement this
                # "run_away": None, # TODO: Implement this
                # "scream_for_help": None, # TODO: Implement this
            }
        }

    def add_trigger(self, trigger: Trigger):
        self.collected_triggers.append(trigger)

    def pop_trigger(self):
        """
        Pops the trigger on 0th index
        """
        return self.collected_triggers.pop(0)

    def get_triggered_triggers(self):
        collected_triggers = self.collected_triggers
        self.collected_triggers = []
        return collected_triggers
    
    def _get_tools(
            self,
            mode: str,
    )->dict:
        tools = dict()
        for k,tool in self.action_map[mode].items():
            tools[k] = create_npc_action_tool(tool, k)
        return tools 
    
    def get_reaction(
            self,
            event: str,
            mode: str,
            additional_tools: dict = {},
            chat_history: List[str] = [],
    ):
        # TODO: if new interaction with player already met, inject historic memory for context
        tools = self._get_tools(mode)
        tools.update(additional_tools)
        self.character.agent.update_tools(tools)
        # perception = self.get_character_perception(event)
        # event = event + "\n\n" + perception
        # print(event)
        final_output = self.character.agent.get_reaction(event, self.character.background, self.character.name, chat_history)
        # TODO: Implement short-term memory update in Game class from Trigger resolutions
        return final_output
    
    def get_character_perception(
            self,
            event: str,
    )->str:
        """
        Get the character's perception of the event.
        """
        system_prompt = NPC_PERCEPTION_SYSTEM_PROMPT.format(
            name = self.character.name,
            personality = self.character.get_personality(),
            beliefs = self.character.get_views_beliefs(),
        )
        response = self._call_model(
            prompt=event,
            system_prompt=system_prompt,
        )
        response = PERCEPTION_FORMAT.format(
            name=self.character.name,
            perception=response,
        )
        return response
    
    def _call_model(
            self,
            prompt: str,
            system_prompt: str,
            max_tokens: int = 200,
    )->str:
        response = self.model.generate(prompt=prompt, max_tokens=max_tokens, system_prompt=system_prompt)
        return response
    
    def _prepare_model(
            self,
            model: StandardGPT,
            model_name: str,
    ):
        return model(model=model_name)

