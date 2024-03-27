from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

ART_SYSTEM_PROMPT = """You are an Art Director for a video game company. You are tasked with creating concept art for a new game.
Given the game events described by the user, create a description of the concept art for the game that accurately reflects the events in the user's description.
Your output should be a detailed description of what you envisage seeing in the image, with thematic tags at the end encased in <theme> tags. For example:
"An epic battle scene with dragons and knights fighting in a medieval castle. <fantasy>, <medieval>, <epic>, <battle>, <dragons>, <knights>"."""

IMAGE_TAGS_PROMPT = """Given the game world narrative provided by the user, generate a list of tags that describe the art style that suits the narrative. 
This should be a comma-separated list of thematic keywords, for example: "fantasy, medieval, dark, gritty"."""

SYSTEM_PROMPTS = {
    "art_system_prompt": ART_SYSTEM_PROMPT,
    "image_tags": IMAGE_TAGS_PROMPT
}

class StandardGPT:

    def __init__(
            self,
            api_key: str = os.environ.get("OPENAI_API_KEY"),
            model: str = "gpt-3.5-turbo",
    ):
        self.api_key = api_key
        self.client = OpenAI()
        self.model = model

    def generate(
            self,
            prompt: str,
            max_tokens: int = 200,
            system_prompt: str = "art_system_prompt"
    ):
        print(str({"role": "system", "content": SYSTEM_PROMPTS[system_prompt]}),'\n',
                str({"role": "user", "content": prompt}))
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS[system_prompt]},
                {"role": "user", "content": prompt}
            ]
        )
        response = response.choices[0].message.content
        print(response)
        return response