from src.game.game import Game
from src.game.configs import GAME_DATA_PATH, GameDataPaths
from src.environments.environment_loaders import (
    EnvironmentLoader, 
    EnvironmentMapLoader, 
    LocalLocationLoader, 
    PositionLoader
)
from src.quests.base import QuestLoader
from src.items.item_loader import ItemLoader
from src.characters.types.npcs.load_npc import NPCLoader
from src.characters.types.player.load_player import PlayerLoader
from src.triggers.trigger_loaders import TriggerLoader

from src.endpoints.image_generation import Dalle

from pathlib import Path
import os
import json
from uuid import uuid4

class GameLoaderException(Exception):
    pass

class GameLoader:

    def __init__(
            self,
            game_data_path: Path=Path(GAME_DATA_PATH),
            player_loader: PlayerLoader=PlayerLoader,
            environment_loader: EnvironmentLoader=EnvironmentLoader,
            environment_map_loader: EnvironmentMapLoader=EnvironmentMapLoader,
            local_location_loader: LocalLocationLoader=LocalLocationLoader,
            position_loader: PositionLoader=PositionLoader,
            trigger_loader: TriggerLoader=TriggerLoader,
            item_loader: ItemLoader=ItemLoader,
            npc_loader: NPCLoader=NPCLoader,
            quest_loader: QuestLoader=QuestLoader,
    ):
        self.game_data_path: Path = game_data_path
        self.data_paths: GameDataPaths = None
        # loaders
        self.player_loader: PlayerLoader = player_loader
        self.environment_loader: EnvironmentLoader = environment_loader
        self.environment_map_loader: EnvironmentMapLoader = environment_map_loader
        self.local_location_loader: LocalLocationLoader = local_location_loader
        self.trigger_loader: TriggerLoader = trigger_loader
        self.position_loader: PositionLoader = position_loader
        self.item_loader: ItemLoader = item_loader
        self.npc_loader: NPCLoader = npc_loader
        self.quest_loader: QuestLoader = quest_loader

    def _load_game_data(
            self
    ):
        with open(self.game_data_path, 'r') as f:
            game_data = json.load(f)
        return game_data
    
    def _load_data_paths(
            self,
            game_data: dict,
            player_id: str
    ):
        data_paths = game_data[player_id]
        return GameDataPaths(**data_paths)

    def _setup_environment_loader(
            self,
            data_paths: GameDataPaths
    ):
        return self.environment_loader(
            environment_data_path=data_paths.environments_data_path,
            environment_map_loader=self.environment_map_loader,
            location_loader=self.local_location_loader,
            position_loader=self.position_loader,
            trigger_loader=self.trigger_loader,
            )
        
    
    def _load_player(
            self,
            player_id: str
    ):
        return self.player_loader.get_player(player_id)

    def _load_loaders(
            self,
            data_paths: GameDataPaths
    ):
        self.trigger_loader = self.trigger_loader(
            data_path=data_paths.triggers_data_path
        )
        
        self.quest_loader = self.quest_loader(
            quest_data_path=data_paths.quest_data_path
        )

        self.player_loader = self.player_loader(
            player_data_path = data_paths.player_data_path,
            trigger_loader=self.trigger_loader,
            quest_loader=self.quest_loader,
            memories_root_dir=data_paths.memories_root_dir
        )

        self.item_loader = self.item_loader(
            data_paths.item_data_path
        )

        self.npc_loader = self.npc_loader(
            data_paths.npc_data_path,
            memories_root_dir=data_paths.memories_root_dir
        )

        self.position_loader = self.position_loader(
            trigger_loader=self.trigger_loader,
            item_loader=self.item_loader,
        )

        self.local_location_loader = self.local_location_loader(
            data_paths.local_locations_data_path
        )

        self.environment_map_loader = self.environment_map_loader(
            data_paths.map_data_path
        )

        self.environment_loader = self._setup_environment_loader(data_paths)

    def _load_environment(
            self,
            location: str
    ):
        return self.environment_loader.get_environment(location)

    def load_game(
            self,
            player_id: str,
    ):
        game_data = self._load_game_data()
        data_paths = self._load_data_paths(game_data, player_id)
        self._load_loaders(data_paths)
        player = self._load_player(player_id)
        environment = self._load_environment(player.current_location)
        return Game(
            player=player,
            environment=environment,
            data_paths=data_paths,
            environment_loader=self.environment_loader,
            item_loader=self.item_loader,
            npc_loader=self.npc_loader,
            trigger_loader=self.trigger_loader,
        )
    
    def _setup_data_paths(
            self,
            player_id: str,
    
    ):
        if not os.path.exists("./saves"):
            os.mkdir("./saves")

        with open(f"./data/game/game.json", 'r') as f:
            data = json.load(f)

        if player_id in data.keys():
            raise GameLoaderException(f"Player with id {player_id} already exists.")

        os.mkdir("./saves/" + player_id.replace(" ", "_"))

        dirs_to_copy = [
        "characters",
        "images",
        ]

        for dir in dirs_to_copy:
            os.mkdir("./saves/" + player_id.replace(" ", "_") + "/" + dir)
            files = os.listdir(f"./data/{dir}")
            for file in files:
                # if file json
                if not file.endswith(".json"):
                    continue
                with open(f"./data/{dir}/{file}", 'r') as f:
                    file_data = json.load(f)
                with open(f"./saves/{player_id.replace(' ', '_')}/{dir}/{file}", 'w') as f:
                    json.dump(file_data, f, indent=4)
        
        os.mkdir("./saves/" + player_id.replace(" ", "_") + "/memories")
        os.mkdir("./saves/" + player_id.replace(" ", "_") + "/audio")
        
        if not os.path.exists("./data/logs"):
            os.mkdir("./data/logs")
        
        data_paths = {
            "item_data_path" : "./data/items/items.json",
            "temp_image_data_path" : "./saves/" + player_id.replace(" ", "_")+"/images/",
            "temp_audio_data_path" : "./saves/" + player_id.replace(" ", "_")+"/audio/",
            "map_data_path" : "./data/environments/map.json",
            "quest_data_path" : "./data/quests/quests.json",
            "npc_data_path" : "./saves/" + player_id.replace(" ", "_")+"/characters/characters.json",
            "local_locations_data_path" : "./data/environments/local_locations.json",
            "triggers_data_path" : "./data/triggers/triggers.json",
            "environments_data_path" : "./data/environments/environments.json",
            "memories_root_dir": "./saves/" + player_id.replace(" ", "_") + "/memories/",
        }

        data[player_id] = data_paths

        with open(f"./data/game/game.json", 'w') as f:
            json.dump(data, f, indent=4)

    def new_game(
            self,
            name: str,
            visual_description: str,
            avatar_image_path: Path = None,
            voice: str = "alloy",
    ):
        self._setup_data_paths(name)
        self._create_player(name, visual_description, avatar_image_path, voice)
        # self._setup_data_paths(name)
        return self.load_game(name)
    
    def _create_player(
            self,
            player_id: str,
            visual_description: str,
            avatar_image_path: Path,
            voice: str,
    ):
        with open(f"./data/player/player.json", 'r') as f:
            data = json.load(f)

        if player_id in data.keys():
            raise GameLoaderException(f"Player with id {player_id} already exists.")
        
        if not avatar_image_path:
            gen = Dalle()
            img = gen.generate(visual_description+"\n<sci-fi> <western> <noir> <gritty>")
            image_file_path = f"./saves/{player_id.replace(' ', '_')}/images/{player_id.replace(' ', '_')}.png"
            img.save(image_file_path)
        else:
            image_file_path = avatar_image_path
        
        data[player_id] = {
            "name": player_id,
            "current_location": "The Room",
            "gold": 100,
            "background": {
                "backstory": "Wyatt Thompson was born in the small town of Dusty Creek, Texas, in 1850. He grew up on a ranch, learning the ways of the land from his father, who was a respected cattle rancher. From a young age, Wyatt showed an aptitude for handling horses and firearms, quickly earning him the nickname \"Ace.\"\n\nAt the age of 17, tragedy struck when Wyatt's family ranch was attacked by a gang of outlaws looking to seize their land. Wyatt's parents were killed in the attack, and he was left to fend for himself. Fuelled by vengeance, Wyatt embarked on a quest to track down the outlaws responsible for his family's demise.",
                "personality": "Wyatt is a stoic and determined individual, with a steely resolve forged by years of hardship and loss. He is fiercely independent and values his freedom above all else. Despite his tough exterior, Wyatt has a compassionate side, especially towards those who have suffered injustice. He is a man of few words, preferring to let his actions speak for him.",
                "views_beliefs": "Wyatt believes in justice, albeit of the frontier variety. He has little faith in the law to protect the innocent, preferring to take matters into his own hands when necessary. He is a firm believer in the code of the West, which values honor, loyalty, and courage above all else. However, Wyatt also understands that sometimes survival means bending the rules, and he's not afraid to get his hands dirty to achieve his goals.\n\nDespite his rough exterior, Wyatt has a strong moral compass and strives to do what he believes is right, even if it means making difficult choices along the way. He harbors a deep distrust of authority figures, particularly those in positions of power who abuse their influence for personal gain.\n\nWyatt's quest for vengeance has consumed much of his life, but deep down, he yearns for a sense of belonging and purpose beyond his vendetta. He longs for a world where justice isn't just a fleeting ideal but a tangible reality for all who seek it.",
                "factions": [
                    "Outlaws",
                    "Lawmen",
                    "Frontiersmen"
                ]
            },
            "visual_description": visual_description,
            "memory": {
                    "long_term": None,
                    "short_term": [],
                    "names": {}
                },
            "avatar": {
                    "image": image_file_path,
                },
            "health": {
                    "status": "HEALTHY",
                    "status_turn_count": 0,
                    "description": "",
                    "scars": []
                },
            "skills": {
                "DEXTERITY": "UNTRAINED",
                "AIM": "UNTRAINED",
                "ATHLETICS": "UNTRAINED",
                "BRAWL": "UNTRAINED",
                "LOCKPICK": "UNTRAINED",
                "MEDICINE": "UNTRAINED",
                "MECHANICS": "UNTRAINED",
                "COMPUTERS": "UNTRAINED",
                "DRIVING": "UNTRAINED",
                "STEALTH": "UNTRAINED",
                "PERCEPTION": "UNTRAINED"
            },
            "backpack": [],
            "equipped_items": {
                "HEAD": None,
                "CHEST": None,
                "LEGS": None,
                "FEET": None,
                "MAIN_HAND": None,
                "OFF_HAND": None
            },
            "with_player": False,
            "voice": voice,
            "quest_log": {
                "active_quest_ids": [],
                "completed_quest_ids": [],
                "completed_trigger_ids": []
            },
            "triggers": []
        }

        with open(f"./data/player/player.json", 'w') as f:
            json.dump(data, f, indent=4)
        
        