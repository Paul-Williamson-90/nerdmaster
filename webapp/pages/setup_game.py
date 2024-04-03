import streamlit as st
import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from webapp.frontend import set_layout
from src.game.game_loader import GameLoader
import time

def header():
    st.title("Setup Game")
    st.write("This is the setup game page.")

def quick_setup():
    loader = GameLoader()
    game = loader.new_game(name = st.session_state["player_name"],
                visual_description = "A tall, thin man with a long face and a receding hairline.",
                avatar_image_path = "./data/images/dummy.png",
                voice = "alloy"
    )
    st.session_state["game"] = game
    st.session_state["narration"], st.session_state["images"] = st.session_state["game"].play()

def main():
    set_layout()

    header()

    st.text_input("Enter your name:", key="player_name", value="Bob")

    if st.button("Quick Setup"):
        with st.spinner("Setting up game..."):
            quick_setup()
        st.success("Game setup complete!")
        st.balloons()
        time.sleep(2)
        st.switch_page("pages/game.py")

if __name__ == "__main__":
    main()