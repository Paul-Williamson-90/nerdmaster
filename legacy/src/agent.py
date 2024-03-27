from src.game import NerdMaster
from src.gpt import StandardGPT
from src.narrator import Narrator

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain import hub
from src.image_generator import ImageGenerator

import os 
from dotenv import load_dotenv

load_dotenv()

CUSTOM_SYSTEM_MESSAGE = """You are a Games Master in a text-based adventure game.
You must create and manage the game world, including the player character, monsters, and non-player characters (NPCs).
Use the tools provided to create and manage the game world, these will change based on the state of the game.
The tools are helpful for deciding what narrative to present to the player, and for managing the player's interactions with the game world.
The game world is persistent, so changes you make will persist between interactions with the player.
Make sure you verify actions the player takes, and provide appropriate responses, including any actions related to inventory of the player, NPCs, or monsters.
Make the game explorative, thrilling, and engaging for the player, including battles, quests, and puzzles."""

DEFAULT_NARRATIVE = """The game world is set in a medieval fantasy world, full of eccentric people and occasionally monsters."""

class NerdMasterAgent:

    def __init__(self,
                 game_world_narrative:str=DEFAULT_NARRATIVE,
                 nerdmaster:NerdMaster=NerdMaster,
                 openai_api_key:str=os.getenv("OPENAI_API_KEY"),
                 image_generator:ImageGenerator=ImageGenerator,
                 narrator:Narrator=Narrator,
                 art_gpt:StandardGPT=StandardGPT,
                 ):
        self.game_world_narrative = game_world_narrative
        self.nerdmaster = nerdmaster()
        self.image_generator = image_generator()
        self.narrator = narrator()
        self.art_gpt = art_gpt()
        self.narrative_tags = self._create_narrative_tags(self.game_world_narrative)
        self.history = []
        self._setup_llm(openai_api_key)
        self._setup_agent()

    def _setup_llm(self, openai_api_key:str):
        self.llm = ChatOpenAI(api_key=openai_api_key)

    def _get_history(self):
        return self.history
    
    def _prepare_narrative(self):
        return f"""
**Here is the game's world narrative**:
{self.game_world_narrative}"""

    def _setup_agent(self,):
        tools, sentients = self.nerdmaster.get_tools_and_sentients()
        self.tools = tools
        self.sentients = sentients
        prompt = hub.pull("hwchase17/openai-tools-agent")
        prompt.messages[0].prompt.template = CUSTOM_SYSTEM_MESSAGE + self._prepare_narrative()
        agent = create_openai_tools_agent(self.llm, tools, prompt)
        self.agent = AgentExecutor(agent=agent, tools=tools, verbose=True)

    def generate_image_prompt(
            self,
            context:str,
            system_prompt:str="art_system_prompt",
            max_tokens:int=100
            ):
        return self.art_gpt.generate(context, max_tokens=max_tokens, system_prompt=system_prompt)
    
    def generate_world_image(self):
        prompt = self.generate_image_prompt(self.game_world_narrative, system_prompt="art_system_prompt")
        return self.image_generator.generate(prompt)
    
    def _create_narrative_tags(self, narrative:str):
        return self.art_gpt.generate(narrative, max_tokens=10, system_prompt="image_tags")
    
    def _get_narrative_tags(self):
        return self.narrative_tags
    
    def generate_image(self):
        history = self.history[1:]
        scenic = self._get_narrative_tags()
        context = '\n'.join(history[-2:]
                ).replace("Human: ","Player: ").replace("AI: ","Narrator: ")
        prompt = f"""Here are the last two events in the game world:
{context}
Now, create an image that reflects the events in the game world.
Remember to include the following tags: {scenic}"""
        prompt = self.generate_image_prompt(prompt, system_prompt="art_system_prompt", max_tokens=150)
        self.image = self.image_generator.generate(prompt)

    def get_image(self):
        return self.image
    
    def narrate_last_response(self):
        self.narrator.generate_speech(self.last_response.replace("AI: ",""))
        self.narrator.play_speech()

    def get_last_response(self):
        return self.last_response

    def invoke(self, user_input:str):
        self._setup_agent()
        assert isinstance(user_input, str), "user_input must be a string"
        assert len(user_input) > 0, "user_input must not be empty"
        history = self._get_history()
        response = self.agent.invoke(
            {
                "input": user_input,
                "chat_history": history+[self.sentients]
            }
        )
        self.history += [f"Human: {user_input}\nAI: {response['output']}\n"]
        self.generate_image()
        self.last_response = response["output"]
        return self.last_response