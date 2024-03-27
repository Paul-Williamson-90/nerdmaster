from openai import OpenAI
from dotenv import load_dotenv
import os
import pygame

load_dotenv()

class Narrator:

    def __init__(
            self,
            api_key:str=os.getenv("OPENAI_API_KEY"),
            model:str="tts-1",
            speech_file_path:str="./audio/speech.mp3"
    ):  
        self.speech_file_path = speech_file_path
        self.api_key = api_key
        self.openai = OpenAI()
        self.model = model

    def generate_speech(self, text:str):
        response = self.openai.audio.speech.create(
            model=self.model,
            voice="alloy",
            input=text
        )
        response.stream_to_file(self.speech_file_path)


    def play_speech(self):
        filename = self.speech_file_path
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy(): 
            pygame.time.Clock().tick(10)
        


