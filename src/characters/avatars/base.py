import numpy as np
from pathlib import Path

from src.characters.avatars.prompts import AVATAR_PROMPT
from src.image_generation import Dalle

class Avatar:

    def __init__(
            self,
            visual_description: str,
            avatar: np.ndarray|Path|None,
            image_model: Dalle = Dalle,
    )->None:
        self.image_model = image_model
        self.visual_description = visual_description
        self.avatar = self._load_avatar(avatar)

    def _load_avatar(
            self,
            avatar: np.ndarray|None,
    )->np.ndarray:
        if avatar:
            if isinstance(avatar, np.ndarray):
                return avatar
            elif isinstance(avatar, Path):
                return np.load(avatar)
        else:
            self.create_avatar()

    def create_avatar(
            self,
    )->np.ndarray:
        prompt = AVATAR_PROMPT.format(self.visual_description)
        response = self._call_image_model(prompt=prompt, size="1024x1024", scale=0.6)
        self.avatar = response

    def get_avatar(
            self,
    )->np.ndarray:
        return self.avatar

    def _call_image_model(
            self,
            prompt: str,
    )->np.ndarray:
        return self.image_model.generate(prompt)