from typing import List, Dict

from src.characters.background import Background
from src.characters.memory.prompts import (
    ADD_TO_LONG_TERM, 
    SEARCH_SHORT_TERM, 
    SEARCH_MEMORY,
    SEARCH_MEMORY_SYSTEM,
)
from src.endpoints.gpt import StandardGPT
from src.characters.memory.memory_agent import MemoryAgent

from pathlib import Path
from uuid import uuid4

from src.game.terms import NarrationType

import re


class Memory:

    def __init__(
            self,
            background: Background,
            long_term: MemoryAgent|Path|None = None,
            short_term: List[str] = [],
            model: StandardGPT = StandardGPT,
            model_name: str = "gpt-3.5-turbo",
            names: Dict[str, str] = {},
    )->None:
        self.long_term_file_path = long_term if isinstance(long_term, Path) else None
        self.background = background
        self.names: Dict[str, str] = names
        self.short_term = short_term
        self.model = model(model=model_name)
        self.long_term = self._load_long_term(long_term)

    def memorise_name(
            self,
            name: str,
    )->None:
        self.names[name] = name

    def add_stranger(
            self,
            name: str,
    )->None:
        self.names[name] = "Stranger"

    def _name_replacement(
            self,
            text: str,
    ):
        for name in self.names.keys():
            text = text.replace(
                f"<{name}>", f"<{self.names[name]}>"
            ).replace(
                f"</{name}>", f"</{self.names[name]}>"
            )
        return text
    
    def _check_new_names(
            self,
            text: str,
    ):
        new_names = re.findall(r"<(.*?)>", text)
        for name in new_names:
            if name not in self.names.keys():
                if name not in [x.value for x in list(NarrationType.__members__.values())]:
                    self.add_stranger(name)

    def parse_names(
            self,
            text: str,
    ):
        self._check_new_names(text)
        text = self._name_replacement(text)  
        return text
    
    def _process_long_term(
            self,
            long_term: Path,
    ):
        with open(long_term, 'r') as file:
            data = file.read()
        for name in self.names.keys():
            data = data.replace(
                f"{name}", f"{self.names[name]}"
            )
        new_file_path = long_term.parent / f"{long_term.stem}_temp{long_term.suffix}"
        with open(new_file_path, 'w') as file:
            file.write(data)
        return new_file_path

    def _load_long_term(
            self,
            long_term: MemoryAgent|Path|None,
    ):
        if long_term:
            if isinstance(long_term, MemoryAgent):
                return long_term
            elif isinstance(long_term, Path):
                new_file_path = self._process_long_term(long_term)
                return MemoryAgent(new_file_path)
        else:
            new_file_path = Path(f"./data/memories/{uuid4()}.txt")
            with open(new_file_path, "w") as f:
                f.write(self.background.__str__())
            self.long_term_file_path = new_file_path
            return MemoryAgent(self.long_term_file_path)

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

    def get_short_term_memory(
            self,
    ):
        return "\n\n".join(self.short_term)
    
    def search_short_term(
            self,
            query: str,
    )->str:
        system_message = SEARCH_SHORT_TERM.format(
            short_term=self._name_replacement('\n'.join(self.short_term)),
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
    
