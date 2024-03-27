from langchain_community.document_loaders.text import TextLoader
from langchain_text_splitters import TokenTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent

from pathlib import Path
from enum import Enum

from dotenv import load_dotenv
import os

load_dotenv()

class ChunkConfigs(Enum):
    CHUNK_SIZE = 1024
    CHUNK_WINDOW = 512

class MemoryAgent:
    
    def __init__(
            self,
            memory_path: Path,
            model_name: str = "gpt-3.5-turbo",
            api_key: str = os.getenv("OPENAI_API_KEY"),
    )->None:
        self.memory_path = memory_path
        self.long_term_str: str = ""
        self.agent: AgentExecutor = None
        self._load_memory(api_key, model_name)

    def _load_memory(
            self,
            api_key: str,
            model_name: str,
    )->None:
        loader = TextLoader(self.memory_path)
        documents = loader.load()
        splitter = TokenTextSplitter(
            model_name=model_name,
            chunk_overlap=ChunkConfigs.CHUNK_WINDOW.value,
            chunk_size=ChunkConfigs.CHUNK_SIZE.value,
        )
        texts = splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings(api_key=api_key)
        db = FAISS.from_documents(texts, embeddings)
        retriever = db.as_retriever()
        tool = create_retriever_tool(
            retriever,
            "search_longterm_memory",
            "Searches and returns excerpts from the character's longterm memory.",
        )
        tools = [tool]
        prompt = hub.pull("hwchase17/openai-tools-agent")
        llm = ChatOpenAI(
            temperature=0,
            api_key=api_key,
            model_name=model_name,
        )
        agent = create_openai_tools_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools)
        self.agent = agent_executor
                                                        
    def add_memory(
            self,
            memory: str,
    )->None:
        self.long_term_str = self.long_term_str + '\n\n' + memory
        with self.memory_path.open('a') as f:
            f.write(memory)

    def search_memory(
            self,
            query: str,
    )->str:
        result = self.agent.invoke(
            {"input": query},
        )
        return result