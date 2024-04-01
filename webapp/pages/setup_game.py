import streamlit as st
import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from webapp.frontend import set_layout
from src.game.game_loader import GameLoader

def header():
    st.title("Setup Game")
    st.write("This is the setup game page.")

def main():
    set_layout()

    header()

    st.text_input("Enter your name:", key="player_name", value="Bob")