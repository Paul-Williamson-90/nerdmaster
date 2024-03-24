import streamlit as st
import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from webapp.frontend import set_layout
from src.agent import NerdMasterAgent
from src.agent import DEFAULT_NARRATIVE

def main():
    set_layout()
    st.title("Setup Game")
    st.write("This is the setup game page.")
    st.text_input("Enter your name:", key="player_name", value="Bob")
    st.text_area("Enter the game world narrative:", key="game_world_narrative", value=DEFAULT_NARRATIVE)
    if len(st.session_state["player_name"]) > 0 and len(st.session_state["game_world_narrative"])>0:
        if st.button("Start Game!", use_container_width=True):
            with st.spinner("Setting up game..."):
                st.session_state["agent"] = NerdMasterAgent(
                    game_world_narrative = st.session_state["game_world_narrative"]
                )
                st.session_state["agent"].invoke(f"Hi, my character is called {st.session_state['player_name']} and I want to play your game.")
                st.session_state["new_response"]=True
                st.session_state["image"] = st.session_state["agent"].generate_world_image()
                st.switch_page("pages/game.py")
    else:
        st.warning("Please enter your name and game world narrative to start the game.")

if __name__ == "__main__":
    main()