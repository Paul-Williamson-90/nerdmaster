from src.characters.base import Character
from src.characters.health import Health, DEFAULT_HEALTH
from src.characters.skills.skill_tree import SkillTree, DEFAULT_SKILL_TREE
from src.characters.backpack import Backpack
from src.characters.equipped import Equipped, DEFAULT_SLOT_ITEMS
from src.characters.background import Background
from src.characters.memory.base import Memory
from src.characters.avatars.base import Avatar
from src.triggers.base import Trigger
from src.agents.npc_agent import NPCAgent
from src.game.terms import GameMode
from src.characters.types.npcs.npc_actions import NPCReActionMap
from src.voices.voice import Voice

from typing import List, Dict
import numpy as np


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
            voice: Voice = Voice, 
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
            agent=agent,
            reactions=reactions,
        )
    
    def character_reaction(
            self,
            additional_tools: dict = {},
            mode: str = GameMode.DIALOGUE.value,
    )->str:
        event = self.get_short_term_memory()
        response = self.reactions.get_reaction(event, mode, additional_tools)
        return response