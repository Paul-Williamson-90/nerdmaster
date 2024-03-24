# Welcome to NerdMaster!

This repo is for a little fun side-project using generative AI to create a completely open-world game that is different with every play.

The only limit is your own imagination!

## How it works
- LangChain Agents act as a Games Master in the background, using player interactions alongside a set of pre-defined tools that control elements of the game environment, such as spawning NPC's, monsters, items, etc.
- OpenAI GPT3.5 is used as an 'Art Director' that tells Dalle-3 what images to create.
- Finally, OpenAI TTS-1 will narrate the final outputs of the LangChain Agent.

## How to play

1. First setup your .env file in the root directory:
```
OPENAI_API_KEY = ...
```

2. Then install the requirements:
```bash
pip install -r requirements.txt
```

3. Then run the game in your browser:
```bash
streamlit run webapp/frontend.py
```

# Happy gaming!