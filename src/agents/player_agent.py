from src.agents.agent import NerdMasterAgent

import os 
from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain import hub

from src.agents.prompts import (
    DEFAULT_EVENT_OUTCOME_FORMAT,
    PLAYER_SYSTEM_PROMPT
)

from src.game.configs import AgentConfigs

load_dotenv()


class PlayerAgent(NerdMasterAgent):

    def __init__(
            self,
            system_message: str = "",
            prompt_id: str = "hwchase17/openai-tools-agent",
            openai_api_key: str = os.getenv("OPENAI_API_KEY"),
            verbose: bool = AgentConfigs.VERBOSE.value,
            event_outcome_format: str = DEFAULT_EVENT_OUTCOME_FORMAT,
            model: str = "gpt-4-turbo-preview"
    )->None:
        super().__init__(system_message, prompt_id, openai_api_key, verbose, event_outcome_format, model)

    def _prepare_system(
            self, 
            name: str
    )->str:
        return PLAYER_SYSTEM_PROMPT.format(
            name=name,
        )

    def _prepare_prompt(
            self, 
            name: str
    )->str:
        prompt = hub.pull(self.prompt_id)
        prompt.messages[0].prompt.template = self._prepare_system(name)
        prompt[2].prompt.template = "**Player Input Request:**\n{input}"
        return prompt

    def _setup_agent(
            self, 
            name: str
    ):
        tools = self._prepare_tools()
        prompt = self._prepare_prompt(name)
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
            user_input: str,
            name: str,
    ):
        self._setup_agent(name)
        response = self.agent.invoke(
            {
                "input": user_input,
                "chat_history": self._get_history(),
            }
        )
        return response["output"]

    def get_reaction(
            self,
            event: str,
            name: str,
    )->str:
        response = self.invoke(event, name)
        return response

    