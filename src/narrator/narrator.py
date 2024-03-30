


class Narration:

    def __init__(
            self,
            text: str|None,
            audio_path: str|None,
            image_path: str|None,
    ):
        self.text = text
        self.audio_path = audio_path
        self.image_path = image_path

    def to_dict(self):
        return {
            "text": self.text,
            "audio_path": self.audio_path,
            "image_path": self.image_path,
        }
    

class Narrator:

    def __init__(
            self
    ):
        self.narration_queue = []

    def add_narration(
            self,
            text: str|None = None,
            audio_path: str|None = None,
            image_path: str|None = None,
    ):
        narration = Narration(
            text=text,
            audio_path=audio_path,
            image_path=image_path,
        )
        self.narration_queue.append(narration)

    def get_narration_queue(self):
        narration_queue = self.narration_queue
        self.narration_queue = []
        return narration_queue