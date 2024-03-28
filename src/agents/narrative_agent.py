from src.agents.agent import NerdMasterAgent

from src.agents.prompts import (
    CUSTOM_SYSTEM_MESSAGE,
    DEFAULT_NARRATIVE,
    DEFAULT_EVENT_OUTCOME_FORMAT
)
import os 
from dotenv import load_dotenv

load_dotenv()

class NarrativeAgent(NerdMasterAgent):
    def __init__(
            self,
            narrative_context: str = DEFAULT_NARRATIVE,
            system_message: str = CUSTOM_SYSTEM_MESSAGE,
            prompt_id: str = "hwchase17/openai-tools-agent",
            openai_api_key: str = os.getenv("OPENAI_API_KEY"),
            verbose: bool = True,
            event_outcome_format: str = DEFAULT_EVENT_OUTCOME_FORMAT,
            model: str = "gpt-3.5-turbo"
    )->None:
        super().__init__(system_message, prompt_id, openai_api_key, verbose, event_outcome_format, model)
        self.narrative_context = narrative_context
    
    def _prepare_system(self):
        return f"""{self.system_message}
**Here is the game's world narrative**:
{self.narrative_context}"""