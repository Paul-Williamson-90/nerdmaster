from src.triggers.base import TriggerResponse, Trigger, Dialogue
from src.characters.base import Character
from src.utils.rolls import normal_roll
from src.configs import DifficultyConfigs
from src.characters.types.prompts import NPC_PERCEPTION_SYSTEM_PROMPT, PERCEPTION_FORMAT
from src.gpt import StandardGPT

from typing import Dict, List, Callable
from langchain.tools import StructuredTool
from langchain.pydantic_v1 import Field, create_model
    
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

def create_npc_action_tool(callable:Callable, name: str):
    method = callable
    args = {k:v for k,v in method.__annotations__.items() if k != "self" and k != "return"}
    doc = method.__doc__
    func_desc = doc[doc.find("<desc>") + len("<desc>"):doc.find("</desc>")]
    arg_desc = dict()
    for arg in args.keys():
        desc = doc[doc.find(f"<{arg}>: ")+len(f"<{arg}>: "):]
        desc = desc[:desc.find("\n")]
        arg_desc[arg] = desc
    arg_fields = dict()
    for k,v in args.items():
        arg_fields[k] = (v, Field(description=arg_desc[k]))

    # Create the new model
    Model = create_model('Model', **arg_fields)

    tool = StructuredTool.from_function(
        func=method,
        name=name,
        description=func_desc,
        args_schema=Model,
        return_direct=False,
    )
    return tool

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

class NPCAction(Trigger):

    def __init__(
            self,
            npc_action_object: NPCReActionMap,
    ):
        self.npc_action_object = npc_action_object


class SearchMemory(NPCAction):

    trigger_map = {}

    def prepare(
            self,
            search_term: str,
    ):
        pass

    def activate(
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
        character = self.npc_action_object.character
        response = character.memory.search_memory(query, character.name)
        return response

class Speak(NPCAction):

    trigger_map = {}

    def prepare(
            self,
            dialogue: str,
    ):
        """
        <desc>Respond to a narrative event with a dialogue</desc>

        Args
        str - <dialogue>: The dialogue your character is responding with.
        """
        self.attributes = {
            "dialogue": dialogue,
        }
        self.npc_action_object.add_trigger(self)
        return f"**Tool Action Accepted**: You will say '{dialogue}' at the end of your turn."

    def activate(
            self,
            dialogue: str,
    ):
        """
        Game logic for activating the trigger
        Triggers a dialogue from the NPC.
        Triggers are resolved by the Game class, post NPC agent output.
        """
        character = self.npc_action_object.character
        return TriggerResponse(
            narrative_message=dialogue,
            triggers = Dialogue().prepare(character=character, dialogue=dialogue)
        )
    


class Attack(NPCAction):
    """
    NPC Action for attacking a character
    """
    trigger_map = {}

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
            "attacking": self.npc_action_object.character.name,
            "defending": character_to_attack,
        }
        self.npc_action_object.add_trigger(self)
        return f"**Tool Action Accepted**: You will attack {character_to_attack} at the end of your turn."

    def activate(
            self,
            attacking: Character,
            defending: Character,
            defending_coverage: bool = False,
    ):
        """
        Game logic for activating the trigger
        Character and target_character are entered by Game using retrieved attributes and matching.
        """
        skill, weapon_name, weapon_modifier = attacking.equipped_items.get_weapon_attack_stats()
        attack_disadvantage = attacking.health.get_roll_modifier()
        attack = attacking.skills.get_modifier(skill) + weapon_modifier - attack_disadvantage

        defense = defending.skills.get_modifier("DEXTERITY") + (1 if defending_coverage else 0)
        defense += defending.health.get_roll_modifier()

        dc = DifficultyConfigs.ATTACK_DC.value

        if normal_roll(dc, attack-defense):
            narrative_message = f"{attacking.name} attacks {defending.name} with their {weapon_name} and hits!\n"
            narrative_message += defending.health.take_damage(narrative_message) # TODO: Implement this on health
            return TriggerResponse(
                narrative_message=narrative_message,
            )
        else:
            narrative_message = f"{attacking.name} attacks {defending.name} with their {weapon_name} and misses!"
            return TriggerResponse(
                narrative_message=narrative_message,
            )



class PrepareAttack(NPCAction):
    """
    NPC Action for preparing to attack a character, initiative roll for who goes first / if the character has a chance to respond
    """
    trigger_map = {
        "Attack": Attack,
    }

    def prepare(self,
                character_to_attack: str,
    )->str:
        """
        <desc>Prepare to attack a character. You should only choose this if it suits your character's narrative in response to the event.</desc>
        """
        self.attributes = {
            "attacking_character": self.npc_action_object.character.name,
            "target_character": character_to_attack,
        }
        self.npc_action_object.add_trigger(self)
        return f"**Tool Action Accepted**: You will prepare to attack {character_to_attack} at the end of your turn."

    def activate(
            self,
            character: Character,
            target_character: Character,
    ):
        """
        Game logic for activating the trigger
        Character and target_character are entered by Game using retrieved attributes and matching.
        """
        character_dex_mod = character.skills.get_modifier("DEXTERITY")
        target_character_dex_mod = target_character.skills.get_modifier("DEXTERITY")
        target_character_perc_mod = target_character.skills.get_modifier("PERCEPTION")
        target_mod = max([target_character_dex_mod, target_character_perc_mod])
        dc = DifficultyConfigs.PREPARE_ATTACK_DC.value

        if normal_roll(dc, character_dex_mod-target_mod):
            prepared_trigger = self.trigger_map["Attack"]()
            narrative_message = f"{character.name} attacks {target_character.name}, {target_character.name} is caught off guard!"
            prepared_trigger.prepare(attacking=character.name, defending=target_character.name)
            return TriggerResponse(
                triggers=prepared_trigger,
                narrative_message=narrative_message,
            )

        else:
            narrative_message = f"{target_character.name} notices {character.name} is about to attack!"
            return TriggerResponse(
                triggers=None,
                narrative_message=narrative_message,
            )

