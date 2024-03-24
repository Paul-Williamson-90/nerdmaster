from typing import List

class Player:

    def __init__(
            self,
            name:str
    ):
        self.name = name
        self.health = 100
        self.inventory = []
        self.gold = 10
        self.tools = [
            self.get_health, 
            self.modify_health, 
            self.get_inventory, 
            self.add_to_inventory, 
            self.remove_from_inventory, 
            self.get_gold, 
            self.modify_gold, 
            self.get_name
        ]

    def get_health(self:object):
        """
        <desc>Returns the amount of health the player has remaining.</desc>
        """
        return f"NerdMaster: {self.name} has {self.health} health remaining."
    
    def modify_health(self:object, amount:int):
        """
        <desc>Use this tool to modify the player's health in response to an event that has occurred in the story.</desc>

        Args:
        int - amount: The amount of health to modify the player's health by.

        Returns:

        """
        assert isinstance(amount, int), "amount must be an integer"
        self.health += amount
        if self.health < 0:
            self.health = 0
        return f"NerdMaster: {self.name} has {self.health} health remaining."
    
    def get_inventory(self:object):
        """
        <desc>Use this tool to get the items in the player's inventory.</desc>

        Returns:
        str: A string listing the items in the player's inventory.
        """
        inventory = '- '
        inventory += '\n- '.join(self.inventory)
        return f"NerdMaster: {self.name} has these items in their inventory:\n{inventory}"
    
    def add_to_inventory(self:object, item:str):
        """
        <desc>Use this tool to add an item to the player's inventory.</desc>

        Args:
        str - item: The item to add to the player's inventory.

        Returns:
        A message confirming the item has been added to the player's inventory.
        """
        assert isinstance(item, str), "item must be a string"
        self.inventory.append(item)
        return f"NerdMaster: {item} has been added to {self.name}'s inventory."
    
    def remove_from_inventory(self:object, item:str):
        """
        <desc>Use this tool to remove an item from the player's inventory.</desc>

        Args:
        str - item: The item to remove from the player's inventory.

        Returns:
        A message confirming the item has been removed from the player's inventory.
        """
        assert isinstance(item, str), "item must be a string"
        self.inventory.remove(item)
        return f"NerdMaster: {item} has been removed from {self.name}'s inventory."
    
    def get_gold(self:object):
        """
        <desc>Use this tool to get the amount of gold the player has.</desc>

        Returns:
        str: A string showing the amount of gold the player has.
        """
        return f"NerdMaster: {self.name} has {self.gold}"
    
    def modify_gold(self:object, amount:int):
        """
        <desc>Use this tool to modify the amount of gold the player has.</desc>

        Args:
        int - amount: The amount of gold to add or remove from the player's gold total.

        Returns:
        str: A message confirming the amount of gold the player now has.
        """
        assert isinstance(amount, int), "amount must be an integer"
        self.gold += amount
        return f"NerdMaster: {self.name} now has {self.gold} gold."
    
    def get_name(self:object):
        """
        <desc>Use this tool to get the name of the player's character.</desc>

        Returns:
        str: The name of the player's character.
        """
        return self.name
    
class NPC(Player):

    def __init__(
            self,
            name:str,
            inventory:List[str]
    ):
        super().__init__(name=name)
        self.inventory = inventory
        
    
class Monster:

    def __init__(
            self,
            name:str,
            equipment:list
    ):
        self.name = name
        self.equipment = equipment
        self.health = 100
        self.tools = [
            self.get_health, 
            self.modify_health, 
            self.get_name
        ]

    def get_health(self:object):
        """
        <desc>Use this tool to get the amount of health the monster has remaining.</desc>

        Returns:
        str: A message showing the amount of health the monster has remaining.
        """
        return f"NerdMaster: {self.name} has {self.health} health remaining."
    
    def modify_health(self:object, amount:int):
        """
        <desc>Use this tool to modify the monster's health in response to an event that has occurred in the story.</desc>

        Args:
        int - amount: The amount of health to modify the monster's health by.

        Returns:
        str: A message showing the amount of health the monster has remaining.
        """
        assert isinstance(amount, int), "amount must be an integer"
        self.health += amount
        if self.health < 0:
            self.health = 0
        return f"NerdMaster: {self.name} has {self.health} health remaining."
    
    def get_name(self:object):
        """
        <desc>Use this tool to get the name of the monster.</desc>

        Returns:
        str: The name of the monster.
        """
        return self.name