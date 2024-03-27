from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain import hub

from typing import List, Dict

from src.agents.prompts import CUSTOM_SYSTEM_MESSAGE, DEFAULT_NARRATIVE
from src.utils.tools import create_tool
import os 
from dotenv import load_dotenv

load_dotenv()

class NerdMasterAgent:
    def __init__(
            self,
            narrative_context: str = DEFAULT_NARRATIVE,
            system_message: str = CUSTOM_SYSTEM_MESSAGE,
            prompt_id: str = "hwchase17/openai-tools-agent",
            openai_api_key: str = os.getenv("OPENAI_API_KEY"),
            verbose: bool = True,
    )->None:
        self.llm: ChatOpenAI = self._setup_llm(openai_api_key)
        self.narrative_context = narrative_context
        self.prompt_id = prompt_id
        self.system_message = system_message
        self.verbose = verbose
        self.last_response: str|None = None
        self.agent: AgentExecutor|None = None
        self.history: List[str|None] = []
        self.tools: Dict[str, StructuredTool|Dict[str, StructuredTool]] = []

    def _setup_llm(
            self, 
            openai_api_key:str
    )->ChatOpenAI:
        return ChatOpenAI(api_key=openai_api_key)
    
    def _prepare_tools(
            self, 
            tools:List[StructuredTool] = []
    )->List[StructuredTool]:
        tools = []
        for _, v in self.tools.items():
            if isinstance(v, dict):
                tools = self._prepare_tools(v, tools)
            else:
                tools += [create_tool(v)]
        return tools
    
    def _get_history(self)->List[str|None]:
        # TODO: control the length of the history
        return self.history
    
    def _prepare_system(self):
        return f"""{self.system_message}
**Here is the game's world narrative**:
{self.narrative_context}"""
    
    def _setup_agent(self):
        tools = self._prepare_tools()
        prompt = hub.pull(self.prompt_id)
        prompt.messages[0].prompt.template = self._prepare_system()
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
    
    def get_last_response(self)->str|None:
        return self.last_response
    
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
        self.history += [f"Human: {user_input}\nAI: {response['output']}\n"]
        self.last_response = response["output"]
        return self.last_response