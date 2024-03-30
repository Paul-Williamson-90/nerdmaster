from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain import hub

from abc import ABC, abstractmethod

from typing import List, Dict

from src.agents.prompts import (
    CUSTOM_SYSTEM_MESSAGE,
    DEFAULT_EVENT_OUTCOME_FORMAT
)
from src.utils.tools import create_tool
import os 
from dotenv import load_dotenv

load_dotenv()

class NerdMasterAgent(ABC):
    def __init__(
            self,
            system_message: str = CUSTOM_SYSTEM_MESSAGE,
            prompt_id: str = "hwchase17/openai-tools-agent",
            openai_api_key: str = os.getenv("OPENAI_API_KEY"),
            verbose: bool = True,
            event_outcome_format: str = DEFAULT_EVENT_OUTCOME_FORMAT,
            model: str = "gpt-4-turbo-preview"
    )->None:
        self.model = model
        self.llm: ChatOpenAI = self._setup_llm(openai_api_key)
        self.prompt_id = prompt_id
        self.system_message = system_message
        self.verbose = verbose
        self.agent: AgentExecutor|None = None
        self.history: List[str|None] = []
        self.event_outcome_format = event_outcome_format
        self.tools: Dict[str, StructuredTool|Dict[str, StructuredTool]] = []

    def _setup_llm(
            self, 
            openai_api_key:str
    )->ChatOpenAI:
        return ChatOpenAI(
            api_key=openai_api_key,
            model=self.model
        )
    
    def update_tools(
            self, 
            tools: dict
    ):
        self.tools = tools
    
    def _prepare_tools(
            self, 
            tools:List[StructuredTool] = []
    )->List[StructuredTool]:
        tools = []
        for _, v in self.tools.items():
            if isinstance(v, dict):
                tools = self._prepare_tools(v, tools)
            else:
                if isinstance(v, StructuredTool):
                    tools += [v]
                else:
                    tools += [create_tool(v)]
        return tools
    
    def _get_history(self)->List[str|None]:
        # TODO: control the length of the history
        return self.history
    
    @abstractmethod
    def _prepare_system(self):
        ...

    def _prepare_prompt(self):
        prompt = hub.pull(self.prompt_id)
        prompt.messages[0].prompt.template = self._prepare_system()
        return prompt
    
    def _setup_agent(self):
        tools = self._prepare_tools()
        prompt = self._prepare_prompt()
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
            user_input:str
    ):
        self._setup_agent()
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

