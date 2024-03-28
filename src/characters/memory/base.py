from typing import List

from src.characters.background import Background
from src.characters.memory.prompts import (
    ADD_TO_LONG_TERM, 
    SEARCH_SHORT_TERM, 
    SEARCH_MEMORY,
    SEARCH_MEMORY_SYSTEM,
)
from src.gpt import StandardGPT
from src.characters.memory.memory_agent import MemoryAgent

from pathlib import Path
import tempfile


class Memory:

    def __init__(
            self,
            background: Background,
            long_term: MemoryAgent|Path|None = None,
            short_term: List[str] = [],
            model: StandardGPT = StandardGPT,
            model_name: str = "gpt-3.5-turbo"
    )->None:
        self.background = background
        self.short_term = short_term
        self.model = model(model=model_name)
        self.long_term = self._load_long_term(long_term)

    def _load_long_term(
            self,
            long_term: MemoryAgent|Path|None,
    ):
        if long_term:
            if isinstance(long_term, MemoryAgent):
                return long_term
            elif isinstance(long_term, Path):
                return MemoryAgent(long_term)
        else:
            with tempfile.NamedTemporaryFile(delete=False) as temp:
                temp.write(self.background.__str__().encode())
                temp_path = temp.name
            return MemoryAgent(temp_path)

    def add_to_short_term(
            self,
            memory: str,
    )->None:
        self.short_term += [memory]

    def add_to_long_term(
            self,
            short_term: str,
    )->None:
        background_str = self.background.__str__()
        prompt = ADD_TO_LONG_TERM.format(
            short_term='\n'.join(short_term),
            background=background_str,
        )
        memory = self._call_model(prompt)
        self.long_term.add_memory(memory)

    def reduce_short_term(
            self,
    )->str:
        self.add_to_long_term("\n".join(self.short_term))
        self.short_term = []
    
    def search_short_term(
            self,
            query: str,
    )->str:
        system_message = SEARCH_SHORT_TERM.format(
            short_term='\n'.join(self.short_term),
        )
        response = self._call_model(query, system_message)
        return response
    
    def search_memory(
            self,
            query: str,
            name: str,
    )->str:
        short_term = self.search_short_term(query)
        long_term = self.long_term.search_memory(query)
        prompt = SEARCH_MEMORY.format(
            query=query,
        )
        system_prompt = SEARCH_MEMORY_SYSTEM.format(
            short_term=short_term,
            long_term=long_term,
            name=name,
        )
        response = self._call_model(prompt=prompt, system_prompt=system_prompt)
        return response
    
    def _call_model(
            self,
            prompt: str,
            system_prompt: str,
            max_tokens: int = 200,
    )->str:
        response = self.model.generate(prompt=prompt, max_tokens=max_tokens, system_prompt=system_prompt)
        return response
    
