from src.agents.agent import NerdMasterAgent
from src.characters.background import Background

import os 
from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain import hub

from src.agents.prompts import (
    CUSTOM_SYSTEM_MESSAGE,
    DEFAULT_EVENT_OUTCOME_FORMAT,
    NPC_SYSTEM_PROMPT
)

load_dotenv()


class NPCAgent(NerdMasterAgent):

    def __init__(
            self,
            system_message: str = CUSTOM_SYSTEM_MESSAGE,
            prompt_id: str = "hwchase17/openai-tools-agent",
            openai_api_key: str = os.getenv("OPENAI_API_KEY"),
            verbose: bool = True,
            event_outcome_format: str = DEFAULT_EVENT_OUTCOME_FORMAT,
    )->None:
        super().__init__(system_message, prompt_id, openai_api_key, verbose, event_outcome_format)

    def _prepare_system(self, background: Background, name: str)->str:
        personality = background.get_personality()
        backstory = background.get_backstory()
        beliefs = background.get_views_beliefs()
        return NPC_SYSTEM_PROMPT.format(
            personality=personality,
            backstory=backstory,
            beliefs=beliefs,
            system=self.system_message,
            name=name,
        )
    
    def update_tools(self, tools: dict):
        self.tools = tools

    def _setup_agent(self, background: Background, name: str):
        tools = self._prepare_tools()
        prompt = hub.pull(self.prompt_id)
        prompt.messages[0].prompt.template = self._prepare_system(background, name)
        prompt[2].prompt.template = "**Event**:\n{input}" # added
        agent = create_openai_tools_agent(
            self.llm, 
            tools, 
            prompt
        )
        self.agent = AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=self.verbose
        )
    
    def invoke(
            self, 
            user_input:str,
            background:Background, 
            name:str,
    ):
        self._setup_agent(background, name)
        history = self._get_history()
        response = self.agent.invoke(
            {
                "input": user_input,
                "chat_history": history
            }
        )
        event_outcome = self.event_outcome_format.format(
            input=user_input,
            output=response["output"]
        )
        self.history += [event_outcome]
        return response["output"]

    def get_reaction(
            self,
            event: str,
            background: Background,
            name: str,
    )->str:
        response = self.invoke(event, background, name)
        return response

    