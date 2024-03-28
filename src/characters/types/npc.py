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
from src.characters.types.npc_actions import NPCReActionMap

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
            voice: str = "alloy", # TODO: Change this for Voice module
            triggers: List[Trigger] = [],
            agent: NPCAgent = NPCAgent,
            reactions: NPCReActionMap = NPCReActionMap,
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
        self.reactions = reactions(self)
        self.action_tool_outputs:List[str]=[]

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
            "get_visual_description": self.get_visual_description,

            # Maybe experiment with re-writing character dialogues against the background
            "get_personality": self.get_personality,

            # Useful for alignment checks
            "get_factions": self.get_factions,
            "check_faction": self.check_faction,

            # Needed for game end
            "get_avatar": self.get_avatar,
        }}
        return tools
    
    def see_items(self)->str:
        """
        <desc>Sees the items in the backpack</desc>
        """
        return self.backpack.show_items_str()
    
    def _parse_event(
            self,
            event: str,
            name: str
    )->str:
        """
        Handles the event string in preparation for sending to the NPC Dialogue Agent.
        """
        event = event.replace("dialogue", name) # TODO: Event needs names instead of <dialogue>
        return event
    
    def character_reaction(
            self,
            event: str,
            additional_tools: dict = {},
            name: str = "Stranger",
            mode: str = "dialogue",
            chat_history: List[str] = []
    )->str:
        event = self._parse_event(event, name)
        response = self.reactions.get_reaction(event, mode, additional_tools, chat_history)
        return response
    