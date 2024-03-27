from src.characters.base import Character
from src.characters.health import Health, DEFAULT_HEALTH
from src.characters.skills.skill_tree import SkillTree, DEFAULT_SKILL_TREE
from src.characters.backpack import Backpack
from src.characters.equipped import Equipped, DEFAULT_SLOT_ITEMS
from src.characters.background import Background
from src.characters.memory.base import Memory
from src.characters.avatars.base import Avatar
from src.triggers.base import Trigger
from src.characters.types.prompts import ATTACK_TEMPLATE
from src.agents.npc_agent import NPCAgent

from typing import List, Dict
import numpy as np

import re

class NPC(Character):

    def __init__(
            self,
            name: str,
            gold: int,
            background: Background|dict,
            visual_description: str,
            memory: Memory|Dict[str, List[str]|str], 
            avatar: Avatar|np.ndarray|None, 
            health: Health|dict = DEFAULT_HEALTH,
            skills: SkillTree|Dict[str, str] = DEFAULT_SKILL_TREE,
            backpack: Backpack|List[str] = [], 
            equipped_items: Equipped|Dict[str, str] = DEFAULT_SLOT_ITEMS, 
            with_player: bool = False,
            voice: str = "alloy",
            triggers: List[Trigger] = [],
            agent: NPCAgent = NPCAgent,
    )->None:
        super().__init__(
            name=name,
            gold=gold,
            background=background,
            visual_description=visual_description,
            memory=memory,
            avatar=avatar,
            health=health,
            skills=skills,
            backpack=backpack,
            equipped_items=equipped_items,
            with_player=with_player,
            voice=voice,
            triggers=triggers,
        )
        self.agent = agent()

    def get_agent_tools(self):
        tools = {
            self.name: {
            # Item Management via click, with narratives sent to AI for generation / logging
            "add_item_to_backpack": self.add_item_to_backpack, # needs to be wrapped in another method game end
            "remove_item_from_backpack": self.remove_item_from_backpack, # needs to be wrapped in another method game end
            "equip_item": self.equip_item, # needs to be wrapped in another method game end
            "unequip_item": self.unequip_item, # needs to be wrapped in another method game end
            "modify_gold": self.modify_gold, # needs to be wrapped in another method game end
            "use_item": self.use_item, # needs to be wrapped in another method game end

            # Faction changes via methods that wrap these
            "add_to_factions": self.add_to_factions,
            "remove_from_factions": self.remove_from_factions,

            # Useful for diaglogues (tell the character about yourself in full)
            # "get_background_full": self.get_background_full,
            # "get_backstory": self.get_backstory,
            "get_visual_description": self.get_visual_description,
            "get_name": self.get_name,

            # Maybe experiment with re-writing character dialogues against the background
            "get_personality": self.get_personality,

            # Useful for alignment checks
            "get_factions": self.get_factions,
            "check_faction": self.check_faction,

            # Memory management
            "add_short_term_memory": self.add_short_term_memory,
            "store_short_term_memory": self.store_short_term_memory,
            # "search_memory": self.search_memory,

            # Needed for game end
            "get_avatar": self.get_avatar,
        }}
        return tools
    
    def see_items(self)->str:
        """
        <desc>Sees the items in the backpack</desc>
        """
        return self.backpack.show_items_str()
    
    def get_npc_agent_tools(self, tools: dict):
        # TODO: add tasks from game/player, such as visual description
        self_tools = {
            "search_memory": self.search_memory,
            "attack_character": self.attack_character,
            "get_name": self.get_name,
            # "see_items": self.see_items,
            # "use_item": self.use_item, 
        }
        tools.update(self_tools)
        return tools
    
    def attack_character(self, character_name: str)->str:
        """
        <desc>Attacks a character</desc>

        args
        str - character_name: The name of the character to attack
        """
        return ATTACK_TEMPLATE.format(
            character_name=character_name,
            name=self.name,
        )
    
    def character_reaction(
            self,
            event: str,
            additional_tools: dict = {},
    )->str:
        """
        <desc>Checks to see what the character's reaction is to a narrative event</desc>

        args:
        str - event: The event that the character is reacting to

        returns:
        str: The character's reaction to the event
        """
        event = event.replace("dialogue","Player") # TODO: Event needs names instead of <dialogue>
        self.agent.update_tools(self.get_npc_agent_tools(additional_tools))
        response = self.agent.get_reaction(
            event=event,
            background=self.background,
            name=self.name,
        )
        # extract any text between <stage> and </stage> tags, or <{self.name}}> and </{self.name}}> tags
        # keeping them in order, into a dict {index: {stage/{self.name}: text}}
        response = re.findall(rf"<(stage|{self.name})>(.*?)</(stage|{self.name})>", response)
        
        response = {index: {"type":tag,
            "text": text} for index, (tag, text, tag2) in enumerate(response)}
        
        formatted_response = ""
        for index in response.keys():
            tag_text = response[index]
            if tag_text["type"] == "stage":
                formatted_response += f"<stage>{tag_text['text']}</stage>\n"
            elif tag_text["type"] == self.name:
                formatted_response += f"<{self.name}>: {tag_text['text']}</{self.name}>\n"
        memory = f"""{event}\n{formatted_response}"""

        self.add_short_term_memory(memory)
        return formatted_response