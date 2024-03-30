from enum import Enum

class GameMode(Enum):

    EXPLORE = "explore"
    INTERACT = "interact"
    TRADE = "trade"
    DIALOGUE = "dialogue"
    COMBAT = "combat"

class Turn(Enum):
    
    PLAYER = "player"
    GAME = "game"
    SAVE = "save"
    NEW_MAP = "new_map"
    QUIT = "quit"

class NarrationType(Enum):

    stage = "stage"
    dialogue = "dialogue"