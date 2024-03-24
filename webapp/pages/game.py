import streamlit as st
import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from webapp.frontend import set_layout


def show_history():
    history = st.session_state["agent"].get_last_response()
    container = st.container(border=True)
    container.subheader("Narrator:")
    container.write(history.replace("AI: ",""))

def player_choice():
    container = st.container(border=True)
    container.text_area("Player: ", key="player_input")
    if st.button("Send", key="send", use_container_width=True):
        st.session_state["agent"].invoke(st.session_state["player_input"])
        st.session_state["new_response"] = True
        st.rerun()

def show_image():
    img = st.session_state["agent"].get_image()
    container = st.container(border=True)
    container.image(img, use_column_width=True)

def play_narration():
    st.session_state["agent"].narrate_last_response()
    st.session_state["new_response"] = False
        

def page_title():
    st.title("NerdMaster")

def main():
    set_layout()
    page_title()
    show_image()
    if st.session_state["new_response"]:
        play_narration()
    show_history()
    player_choice()

if __name__ == "__main__":
    main()