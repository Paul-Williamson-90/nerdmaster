from abc import ABC
from typing import List, Dict
import numpy as np

from src.characters.health import Health, DEFAULT_HEALTH
from src.characters.skills.skill_tree import SkillTree, DEFAULT_SKILL_TREE
from src.characters.backpack import Backpack
from src.characters.equipped import Equipped, DEFAULT_SLOT_ITEMS
from src.characters.background import Background
from src.characters.prompts import VISUAL_DESCRIPTION
from src.characters.memory.base import Memory
from src.characters.avatars.base import Avatar
from src.agents.npc_agent import NPCAgent
from src.agents.player_agent import PlayerAgent
from src.triggers.base import Trigger
from src.voices.voice import Voice
from src.characters.actions.base import ReActionMap

class Character(ABC):

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
            agent: NPCAgent|PlayerAgent = NPCAgent,
            triggers: List[Trigger] = [],
            reactions: ReActionMap = ReActionMap,
    )->None:
        self.name = name
        self.voice: Voice = voice
        self.visual_description = visual_description
        self.backpack: Backpack = self._handle_backpack(backpack)
        self.equipped_items: Equipped = self._handle_equipped_items(equipped_items)
        self.gold = gold
        self.health: Health = self._handle_health(health)
        self.background: Background = self._handle_background(background)
        self.memory: Memory = self._handle_memory(memory)
        self.avatar: Avatar = self._handle_avatar(avatar)
        self.with_player = with_player
        self.skills: SkillTree = self._handle_skills(skills)
        self.triggers = triggers
        self.agent: NPCAgent|PlayerAgent = agent()
        self.reactions: ReActionMap = reactions(self)
        self.action_queue: List[Trigger] = []

    def get_short_term_memory(
            self,
    ):
        return self.memory.get_short_term_memory()

    def add_to_action_queue(
            self,
            trigger: Trigger,
    ):
        self.action_queue.append(trigger)

    def get_action_queue(
            self,
    )->List[Trigger]:
        action_queue = self.action_queue
        self.action_queue = []
        return action_queue
        
    def _handle_avatar(
            self,
            avatar: Avatar|np.ndarray|None,
    )->Avatar:
        if isinstance(avatar, Avatar):
            return avatar
        return Avatar(avatar=avatar, visual_description=self.visual_description)
    
    def create_avatar(self):
        self.avatar.create_avatar()
    
    def get_avatar(self):
        return self.avatar.get_avatar()
    
    def _handle_memory(
            self,
            memory: Memory|Dict[str, List[str]|str],
    )->Memory:
        if isinstance(memory, Memory):
            return memory
        return Memory(**memory)

    def _handle_skills(
            self,
            skills: SkillTree|Dict[str, str],
    )->SkillTree:
        if isinstance(skills, SkillTree):
            return skills
        return SkillTree(skills=skills)

    def _handle_health(
            self,
            health: Health|dict,
    )->Health:
        if isinstance(health, Health):
            return health
        return Health(**health)

    def _handle_background(
            self,
            background: Background|dict,
    )->Background:
        if isinstance(background, Background):
            return background
        return Background(**background)

    def add_item_to_backpack(
            self,
            item_id: str
    )->str:
        """
        <desc>Add an item to the character's backpack.</desc>

        Args:
        str - item_id: The id of the item to add to the backpack.
        """
        status, message = self.backpack.add_item(item_id)
        message += " backpack"
        return message
    
    def remove_item_from_backpack(
            self,
            item_id: str
    )->str:
        """
        <desc>Remove an item from the character's backpack.</desc>

        Args:
        str - item_id: The id of the item to remove from the backpack.
        """
        status, message = self.backpack.remove_item(item_id)
        message += " backpack"
        return message
    
    def _equip_item_checks(
            self,
            item_id: str,
    )->tuple[bool, str]:
        if item_id not in [x.item_id for x in self.backpack.items]:
            return False, "Item not in backpack"
        # equipable
        item_stats = self.backpack.get_item_stats(item_id)
        if not item_stats.equipable:
            return False, "Item not equipable"
        # skill check
        if not item_stats.equip_skill_check(self.skills):
            return False, "Insufficient proficiency to equip item"
        # mass check
        slot = item_stats.equip_slot
        mass = item_stats.mass
        equipped_item_id = self.equipped_items.get_equipped_item_id_by_slot(slot)
        if equipped_item_id:
            equipped_item = self.backpack.get_item_stats(equipped_item_id)
            if not self.backpack.add_item_mass_check(equipped_item, mass):
                return False, "Not enough capacity in backpack to unequip item in replace of item to equip"
        return True, ""
    
    def equip_item(
            self,
            item_id: str
    )->str:
        """
        <desc>Equip an item from the character's backpack.</desc>

        Args:
        str - item_id: The id of the item to equip from the backpack.
        """
        status, message = self._equip_item_checks(item_id)
        if not status:
            return message
        status, message, id_unequipped = self.equipped_items.equip_item(item_id)
        if id_unequipped:
            self.add_item_to_backpack(id_unequipped)
        status, message = self.backpack.remove_item(item_id)
        message += " equipped items"
        return message
    
    def unequip_item(
            self,
            slot: str
    )->str:
        """
        <desc>Unequip an item from the character's equipped items.</desc>

        Args:
        str - slot: The slot of the item to unequip from the equipped items.
        """
        equipped_item_id = self.equipped_items.get_equipped_item_id_by_slot(slot)
        if not equipped_item_id:
            return "No item equipped in slot"
        equipped_item = self.backpack.get_item_stats(equipped_item_id)
        equipped_item_mass = equipped_item.mass
        if not self.backpack.add_item_mass_check(equipped_item_mass):
            return "Not enough capacity in backpack to unequip item"
        status, message, id_unequipped = self.equipped_items.unequip_item(slot)
        if id_unequipped:
            message+=self.add_item_to_backpack(id_unequipped)
        return message

    def modify_gold(
            self, 
            amount: int
    )->tuple[bool, str]:
        """
        <desc>Modify the character's gold.</desc>

        Args:
        int - amount: The amount of gold to add to the character's gold.
        """
        updated_gold = self.gold + amount
        if updated_gold < 0:
            return False, "Insufficient gold"
        self.gold = updated_gold
        return True, f"{amount} gold added, {self.name} now has {updated_gold} gold"

    def _handle_equipped_items(
            self,
            equipped_items: Equipped|Dict[str, str],
    )->Equipped:
        if isinstance(equipped_items, Equipped):
            return equipped_items
        return Equipped(slot_items=equipped_items)

    def _handle_backpack(
            self,
            backpack: Backpack|List[str],
    )->Backpack:
        if isinstance(backpack, Backpack):
            return backpack
        return Backpack(item_ids=backpack)
    
    def get_background_full(self):
        """
        <desc>Get the full background of the character.</desc>
        """
        return self.background.__str__()
    
    def get_factions(self):
        """
        <desc>Get a list of factions the character belongs to.</desc>
        """
        return self.background.get_factions()
    
    def check_faction(self, faction: str):
        """
        <desc>Check if the character belongs to a faction.</desc>

        Args:
        str - faction: The faction to check if the character belongs to.
        """
        if faction in self.get_factions():
            return True
        return False
    
    def get_backstory(self):
        """
        <desc>Get the backstory of the character.</desc>
        """
        return self.background.get_backstory()
    
    def get_personality(self):
        """
        <desc>Get the personality of the character.</desc>
        """
        return self.background.get_personality()
    
    def get_views_beliefs(self):
        """
        <desc>Get the views and beliefs of the character.</desc>
        """
        return self.background.get_views_beliefs()
    
    def add_to_factions(self, addition: str):
        """
        <desc>Add the character to a faction.</desc>
        """
        return self.background.add_to_factions(addition)
    
    def remove_from_factions(self, addition: str):
        """
        <desc>Remove the character from a faction.</desc>
        """
        return self.background.remove_from_factions(addition)
    
    def get_visual_description(self)->str:
        """
        <desc>Get a visual description of the character to send to a character.</desc>

        Returns:
        str: The visual description of the character.
        """
        equipped_description = self.equipped_items.get_equipped_items_str()
        description = VISUAL_DESCRIPTION.format(
            visual_description=self.visual_description,
            equipped_description=equipped_description,
        )
        return description
    
    def get_name(self):
        """
        <desc>Get the name of your own character.</desc>
        """
        return self.name
    
    def add_short_term_memory(
            self,
            memory: str
    )->str:
        """
        <desc>Add a memory to the character's short term memory.</desc>
        """
        self.memory.add_to_short_term(memory)
        
    def store_short_term_memory(
            self,
    )->str:
        """
        <desc>Store the character's short term memory into long term memory.</desc>
        """
        self.memory.reduce_short_term()

    def search_memory(
            self,
            query: str
    )->str:
        """
        <desc>Search your own character's memory using a question. For example, "Do I remember anything regarding..."</desc>

        Args
        str - <query>: The query/thought/question to search your own character's memory with.
        """
        return self.memory.search_memory(query, self.name)
    
    def use_item(
            self,
            unique_id: str,
            character_name: str,
    )->str:
        """
        <desc>Use an item on a character. It is wise to see what items you have first before using this tool.</desc>

        Args:
        str - <unique_id>: The id of the item to use on the character.
        str - <character_name>: The name of the character to use the item on.
        """
        return self.backpack.use_item_by_unique_id(unique_id, character_name)

   