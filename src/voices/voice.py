from openai import OpenAI
# from dotenv import load_dotenv
from pathlib import Path
from uuid import uuid4
from src.game.configs import TEMP_AUDIO_DATA_PATH

# load_dotenv()

class Voice:

    def __init__(
            self,
            voice: str = "alloy",
            model: str = "tts-1",
            audio_data_path: Path = Path(TEMP_AUDIO_DATA_PATH),
    ):
        self.openai = OpenAI()
        self.audio_data_path = audio_data_path
        self.voice = voice
        self.model = model

    def generate(
            self,
            text: str,
    ):
        file_path = str(self.audio_data_path.joinpath(f"{uuid4()}.mp3"))
        response = self.openai.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text
        )
        response.stream_to_file(file_path)

        return Path(file_path)