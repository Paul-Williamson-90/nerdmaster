from openai import OpenAI
from dotenv import load_dotenv
import os
import pygame
from typing import List
from src.configs import TEMP_AUDIO_DATA_PATH

load_dotenv()

class Narrator:

    def __init__(
            self,
            api_key:str=os.getenv("OPENAI_API_KEY"),
            model:str="tts-1",
    ):  
        self.api_key = api_key
        self.openai = OpenAI()
        self.model = model

    def generate_speech(
            self, 
            text:str, 
            voice:str="alloy",
            file_path:str=TEMP_AUDIO_DATA_PATH,
    ):
        response = self.openai.audio.speech.create(
            model=self.model,
            voice=voice,
            input=text
        )
        response.stream_to_file(file_path)


    def play_speech(
            self,
            file_path:str|List[str]=TEMP_AUDIO_DATA_PATH,
    ):
        if isinstance(file_path, str):
            file_path = [file_path]
        for path in file_path:
            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy(): 
                pygame.time.Clock().tick(10)
        


