from src.characters.base import Character
from src.characters.health import Health, DEFAULT_HEALTH
from src.characters.skills.skill_tree import SkillTree, DEFAULT_SKILL_TREE
from src.characters.backpack import Backpack
from src.characters.equipped import Equipped, DEFAULT_SLOT_ITEMS
from src.characters.background import Background
from src.characters.memory.base import Memory
from src.characters.avatars.base import Avatar
from src.triggers.base import Trigger
from src.quests.base import QuestLog
from src.agents.player_agent import PlayerAgent
from src.voices.voice import Voice
from src.characters.types.player.player_actions import PlayerReActionMap


from typing import List, Dict
import numpy as np


class Player(Character):

    def __init__(
            self,
            name: str,
            current_location: str,
            gold: int,
            background: Background|dict,
            visual_description: str,
            memory: Memory|Dict[str, List[str]|str], 
            avatar: Avatar|np.ndarray|None, 
            game = None,
            health: Health|dict = DEFAULT_HEALTH,
            skills: SkillTree|Dict[str, str] = DEFAULT_SKILL_TREE,
            backpack: Backpack|List[str] = [], 
            equipped_items: Equipped|Dict[str, str] = DEFAULT_SLOT_ITEMS, 
            with_player: bool = False,
            voice: Voice = Voice,
            triggers: List[Trigger] = [],
            quest_log: QuestLog = QuestLog([], [], []),
            agent: PlayerAgent = PlayerAgent,
            reactions: PlayerReActionMap = PlayerReActionMap,
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
        self.game = game
        self.current_location = current_location
        self.quest_log = quest_log

    def save(self):
        return {
            "name": self.name,
            "current_location": self.current_location,
            "gold": self.gold,
            "background": {
                "backstory": self.background.backstory,
                "personality": self.background.personality,
                "views_beliefs": self.background.views_beliefs,
                "factions": self.background.factions,
            },
            "visual_description": self.visual_description,
            "memory": {
                "long_term": self.memory.long_term_file_path,
                "short_term": self.memory.short_term,
                "names": self.memory.names,
            },
            "avatar": self.avatar.avatar_path,
            "health": {
                "status": self.health.status,
                "status_turn_count": self.health.status_turn_count,
                "description": self.health.description,
                "scars": self.health.scars,
            },
            "skills": self.skills.serialize(),
            "backpack": self.backpack.items,
            "equipped_items": self.equipped_items.serialize(),
            "with_player": self.with_player,
            "voice": self.voice.voice,
            "triggers": [x.trigger_id for x in self.triggers],
            "quest_log": {
                "active_quest_ids": self.quest_log.active_quest_ids,
                "completed_quest_ids": self.quest_log.completed_quest_ids,
                "completed_trigger_ids": self.quest_log.completed_trigger_ids,
            }
        }
    