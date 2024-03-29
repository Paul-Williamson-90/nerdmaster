import pygame
from pathlib import Path


def play_audio(
        file_path:Path,
):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy(): 
        pygame.time.Clock().tick(10)