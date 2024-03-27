from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class StandardGPT:

    def __init__(
            self,
            system_prompt: str,
            api_key: str = os.environ.get("OPENAI_API_KEY"),
            model: str = "gpt-3.5-turbo",
    ):
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.client = OpenAI()
        self.model = model

    def generate(
            self,
            prompt: str,
            max_tokens: int = 200,
    ):
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        response = response.choices[0].message.content
        return response