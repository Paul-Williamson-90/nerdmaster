from typing import List, Callable
from langchain.tools import StructuredTool
from langchain.pydantic_v1 import Field, create_model
import random

from src.sentients import Player, Monster, NPC
from src.utils import create_tool


class NerdMaster:

    history: list = []
    player: Player
    monsters: list = []
    npcs: list = []
    tools: dict = {}

    def __init__(
            self,
        ):
        self.tools={
            "game_management":{
                "player_setup": self.create_tool(self.setup_player),
            },
            "player":{
            },
            "monsters":{
            },
            "npcs":{
            }
        }

    def create_tool(self, callable:Callable):
        method = callable
        args = {k:v for k,v in method.__annotations__.items() if k != "self"}
        name = method.__name__
        doc = method.__doc__
        func_desc = doc[doc.find("<desc>") + len("<desc>"):doc.find("</desc>")]
        arg_desc = dict()
        for arg in args.keys():
            desc = doc[doc.find(f"{arg}: ")+len(f"{arg}: "):]
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
    
    def roll_dice(self:object, difficulty:int):
        """
        <desc>Use this tool to roll a number between 0 and 100.</desc>

        Args:
        int - difficulty: The number the roll must beat to be successful, must be between 0 and 100.

        Returns:
        str: A message showing the result of the roll.
        """
        assert 0 <= difficulty <= 100, "difficulty must be between 0 and 100"
        roll = random.randint(0, 100)
        if roll >= difficulty:
            return f"NerdMaster: The roll was {roll}. Success!"
        else:
            return f"NerdMaster: The roll was {roll}. Failure."
    
    def get_sentients(self):
        sentients = "**Current Monsters and NPC's in the game**:"
        sentients += "**Monsters**:"
        for monster in self.monsters:
            sentients += f"\n- {monster.name}"
        sentients += "**NPCs**:"
        for npc in self.npcs:
            sentients += f"\n- {npc.name}"
        return sentients
    
    def get_tools_and_sentients(self):
        return (self.get_tools_recursion(tools=self.tools, tools_list=[]),
                self.get_sentients())
    
    def get_tools_recursion(self, tools:dict, tools_list:List[StructuredTool] = []):
        # get all tools
        for _,v in tools.items():
            if isinstance(v, dict):
                tools_list = self.get_tools_recursion(v, tools_list)
            else:
                tools_list += [v]
        return tools_list
    
    def _remove_tool(self,
        tool_categories:List[str],
        tool_name:str,
        ):
        tools = self.tools
        for category in tool_categories:
            tools = tools[category]
        tools.pop(tool_name)
    
    def _add_tool(self, 
        tool: Callable,
        tool_categories:List[str],
        tool_name:str,
        ):
        tools = self.tools
        for category in tool_categories:
            if category not in tools.keys():
                tools[category] = {}
            tools = tools[category]
        tools[tool_name] = create_tool(tool)

    def _remove_tools(
            self,
            tools_categories:List[str],
            tools_names:List[str]=None,
    ):
        if tools_names is None:
            for category in tools_categories:
                self.tools.pop(category)
        else:
            for tool_name in tools_names:
                self._remove_tool(tools_categories, tool_name)

    def _add_tools(
            self,
            tools:List[Callable],
            tools_categories:List[str],
            tools_names:List[str],
    ):
        for tool, tool_name in zip(tools, tools_names):
            self._add_tool(tool, tools_categories, tool_name)
    
    def setup_player(self:object, name:str):
        """
        <desc>Use this tool to create the player's character and begin the game.</desc>

        Args:
        str - name: The name of the player's character.

        Returns:
        str: A message confirming the player's character has been created.
        """
        self.player = Player(name=name)
        # remove the setup player tool
        self._remove_tool(["game_management"], "player_setup")
        # add player tools
        self._add_tools(self.player.tools, ["player"], [tool.__name__ for tool in self.player.tools])
        self._add_tools([self.create_monster], ["monsters"], [self.create_monster.__name__])
        self._add_tools([self.create_npc], ["npcs"], [self.create_npc.__name__])
        return f"NerdMaster: Player created with name {name}."
    
    def create_monster(self:object, name:str, equipment:List[str]):
        """
        <desc>Use this tool to create a monster that the player must engage in battle with.</desc>

        Args:
        str - name: The name of the monster.
        List[str] - equipment: The equipment the monster has.
        """
        monster = Monster(name=name, equipment=equipment)
        self.monsters.append(monster)
        self._add_tools(monster.tools, ["monster", monster.name], [tool.__name__ for tool in monster.tools])
        self._add_tools([self.remove_monster_from_game], ["game_management"], [self.remove_monster_from_game.__name__])
        return f"NerdMaster: Monster created called {name}, with equipment: {equipment}."
    
    def create_npc(self:object, name:str, inventory:List[str]):
        """
        <desc>Use this tool to create a non-player character (NPC) that the player can interact with.</desc>

        Args:
        str - name: The name of the NPC.
        List[str] - inventory: The items the NPC has in their inventory.

        Returns:
        str: A message confirming the NPC has been created.
        """
        npc = NPC(name=name, inventory=inventory)
        self._add_tools(npc.tools, ["npcs", npc.name], [tool.__name__ for tool in npc.tools])
        self._add_tools([self.remove_npc_from_game], ["game_management"], [self.remove_npc_from_game.__name__])
        return f"NerdMaster: NPC created called {name}, with inventory: {inventory}."
    
    def remove_monster_from_game(self:object, name:str):
        """
        <desc>Use this tool to remove a monster from the game.</desc>

        Args:
        str - name: The name of the monster to remove.

        Returns:
        str: A message confirming the monster has been removed from the game.
        """
        for monster in self.monsters:
            if monster.name == name:
                monster_tools = monster.tools 
                for tool in monster_tools:
                    self._remove_tool(["monster", monster.name], tool.__name__)
                self.monsters.remove(monster)
                return f"NerdMaster: Monster {name} has been removed from the game."
        return f"NerdMaster Error: Monster {name} is not in the game."
    
    def remove_npc_from_game(self:object, name:str):
        """
        <desc>Use this tool to remove an NPC from the game.</desc>

        Args:
        str - name: The name of the NPC to remove.

        Returns:
        str: A message confirming the NPC has been removed from the game.
        """
        for npc in self.npcs:
            if npc.name == name:
                npc_tools = npc.tools 
                for tool in npc_tools:
                    self._remove_tool(["npc", npc.name], tool.__name__)
                self.npcs.remove(npc)
                return f"NerdMaster: NPC {name} has been removed from the game."
        return f"NerdMaster Error: NPC {name} is not in the game."