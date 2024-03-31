from src.game.configs import NPC_DATA_PATH
from src.characters.health import Health
from src.characters.skills.skill_tree import SkillTree
from src.characters.backpack import Backpack
from src.characters.equipped import Equipped
from src.characters.background import Background
from src.characters.memory.base import Memory
from src.characters.avatars.base import Avatar
from src.triggers.trigger_loaders import TriggerLoader
from src.characters.types.npcs.npc import NPC
from src.voices.voice import Voice

from copy import deepcopy

import json
from pathlib import Path

class NPCLoader:

    def __init__(
            self,
            data_path: Path = Path(NPC_DATA_PATH),
            trigger_loader: TriggerLoader = TriggerLoader,
            memories_root_dir: Path = Path("./data/memories/"),
    ):
        self.memories_root_dir = memories_root_dir
        self.data_path = data_path
        self.data = self._load_data(data_path)
        self.trigger_loader = trigger_loader()

    def load_character(
            self,
            character_name: str
    )->NPC:
        return self._create_character(character_name)

    def _load_data(self, data_path:Path):
        with open(data_path, "r") as file:
            data = json.load(file)
        return data

    def _create_character(
            self, 
            character_name
    ):
        character_data = deepcopy(self.data[character_name])
        character_data["background"] = Background(
            backstory = character_data["background"]["backstory"],
            personality = character_data["background"]["personality"],
            views_beliefs=character_data["background"]["views_beliefs"],
            factions=character_data["background"]["factions"],
        )
        character_data["memory"] = Memory(background=character_data["background"],
                                          memories_root_dir=self.memories_root_dir,
                                        **character_data["memory"])
        character_data["avatar"] = Avatar(visual_description=character_data["visual_description"],
                                        avatar=character_data["avatar"]["image"])
        character_data["health"] = Health(**character_data["health"])
        character_data["skills"] = SkillTree(skills=character_data["skills"])
        character_data["backpack"] = Backpack(item_ids=character_data["backpack"])
        character_data["equipped_items"] = Equipped(slot_items=character_data["equipped_items"])
        character_data["triggers"] = [self.trigger_loader.get_trigger(trigger_id=trigger) 
                                      for trigger in character_data["triggers"]]
        character_data["voice"] = Voice(voice=character_data["voice"])

        npc = NPC(**character_data)
        return npc

    def character_save(
            self,
            name: str,
            data: dict,
    ):
        self.data[name] = data
        self._save_data()

    def _save_data(self):
        with open(self.data_path, "w") as file:
            json.dump(self.data, file, indent=4)
