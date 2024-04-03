from pathlib import Path

class Avatar:

    def __init__(
            self,
            visual_description: str,
            avatar: Path|None,
    )->None:
        self.visual_description = visual_description
        self.avatar_path = avatar
        self.avatar = avatar

    def get_avatar(
            self,
    )->Path:
        return self.avatar