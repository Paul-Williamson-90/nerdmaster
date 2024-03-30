from src.characters.types.player.player import Player
from src.characters.background import Background
from src.characters.memory.base import Memory
from src.characters.avatars.base import Avatar
from src.characters.health import Health
from src.characters.skills.skill_tree import SkillTree
from src.characters.backpack import Backpack
from src.characters.equipped import Equipped
from src.triggers.trigger_loaders import TriggerLoader
from src.quests.base import QuestLoader
from src.voices.voice import Voice
from src.game.configs import PLAYER_DATA_PATH

from pathlib import Path
import json


class PlayerLoader:

    def __init__(
            self,
            player_data_path: Path = Path(PLAYER_DATA_PATH),
            trigger_loader: TriggerLoader=TriggerLoader,
            quest_loader: QuestLoader=QuestLoader,
    ):
        self.player_data = self._load_player_data(player_data_path)
        self.trigger_loader = trigger_loader()
        self.quest_loader = quest_loader()

    def _load_player_data(
            self,
            player_data_path: Path
    ):
        with open(player_data_path, 'r') as file:
            player_data = json.load(file)
        return player_data
    
    def _get_player_data(
            self, 
            player_id: str
    ):
        return self.player_data[player_id]
    
    def _get_background(
            self,
            player_data: dict
    ):
        data = player_data["background"]
        return Background(
            backstory=data["backstory"],
            personality=data["personality"],
            views_beliefs=data["views_beliefs"],
            factions=data["factions"]
        )
    
    def _get_memory(
            self,
            player_data: dict,
            background: Background,
    ):
        data = player_data["memory"]
        return Memory(
            background=background,
            long_term=data["long_term"],
            short_term=data["short_term"]
        )
    
    def _load_avatar(
            self,
            player_data: dict
    ):
        return Avatar(
            visual_description=player_data["visual_description"],
            avatar=player_data["avatar"]["image"]
        )
    
    def _load_health(
            self,
            player_data: dict
    ):
        data = player_data["health"]
        return Health(
            status=data["status"],
            status_turn_count=data["status_turn_count"],
            description=data["description"],
            scars=data["scars"]
        )
    
    def _load_skills(
            self,
            player_data: dict
    ):
        return SkillTree(
            skills=player_data["skills"]
        )
    
    def _load_backpack(
            self,
            player_data: dict
    ):
        return Backpack(
            item_ids=player_data["backpack"]
        )
    
    def _load_equipped_items(
            self,
            player_data: dict
    ):
        return Equipped(
            slot_items=player_data["equipped_items"]
        )
    
    def _load_triggers(
            self,
            player_data: dict
    ):
        return [self.trigger_loader.get_trigger(trigger_id=trigger) 
                for trigger in player_data["triggers"]]
    
    def _load_quests(
            self,
            player_data: dict
    ):
        return self.quest_loader.load_quest_log(player_data["quest_log"])
    
    def _load_voice(
            self,
            player_data: dict
    ):
        return Voice(
            voice=player_data["voice"]
        )

    def get_player(
            self, 
            player_id: str
    ) -> Player:
        player_data = self._get_player_data(player_id)
        background = self._get_background(player_data)
        memory = self._get_memory(player_data, background)
        quest_load = self._load_quests(player_data)
        avatar = self._load_avatar(player_data)
        health = self._load_health(player_data)
        skills = self._load_skills(player_data)
        backpack = self._load_backpack(player_data)
        equipped_items = self._load_equipped_items(player_data)
        triggers = self._load_triggers(player_data)
        voice = self._load_voice(player_data)
        player = Player(
            name=player_data["name"],
            current_location=player_data["current_location"],
            gold=player_data["gold"],
            background=background,
            visual_description=player_data["visual_description"],
            memory=memory,
            avatar=avatar,
            health=health,
            skills=skills,
            backpack=backpack,
            equipped_items=equipped_items,
            with_player=player_data["with_player"],
            triggers=triggers,
            quest_log=quest_load,
            voice=voice
        )
        return player