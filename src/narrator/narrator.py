from typing import List


class Narration:

    def __init__(
            self,
            text: str|None,
            audio_path: str|None,
            image_path: str|None,
            source: str = None
    ):
        self.text = text
        self.audio_path = audio_path
        self.image_path = image_path
        self.source = source

    def to_dict(self):
        return {
            "text": self.text,
            "audio_path": self.audio_path,
            "image_path": self.image_path,
            "source": self.source
        }
    

class Narrator:

    def __init__(
            self
    ):
        self.narration_queue: List[Narration] = []

    def add_narration(
            self,
            text: str|None = None,
            audio_path: str|None = None,
            image_path: str|None = None,
            source: str = None,
    ):
        narration = Narration(
            text=text,
            audio_path=audio_path,
            image_path=image_path,
            source=source
        )
        self.narration_queue.append(narration)

    def get_narration_queue(
            self
    ):
        narration_queue = self.narration_queue
        self.narration_queue = []
        return [x.to_dict() for x in narration_queue]
    
    def get_one_narration(
            self
    ):
        if self.narration_queue:
            return self.narration_queue.pop(0)
        return None