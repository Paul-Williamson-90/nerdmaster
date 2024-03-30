import pygame
from pathlib import Path
import time


def play_audio(
        file_path:Path,
):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy(): 
        # pygame.time.Clock().tick(10)
        time.sleep(0.1)
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    time.sleep(1.5)

def play_audio_then_delete_file(
        file_path:Path,
):
    play_audio(file_path)
    file_path.unlink(
)