import streamlit as st
import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from webapp.frontend import (
    set_layout, 
    page_layout, 
    get_visual_content_dividers, 
    get_item_mode_dividers, 
    insert_text_content, 
    player_input_area, 
    top_navigation
)

def player_input(text_inputs_area):
    text_inputs_area.text_area("Enter your text here:", key="player_text", value="")
    if st.button("Submit"):
        narration, images = st.session_state["game"].play(
            player_input=st.session_state["player_text"]
        )

        st.session_state["narration"] = narration
        st.session_state["images"] = images
        st.rerun()

def set_background_image():
    st.session_state["images"]["environment"]


def set_player_image(player_viz):
    player_viz.image(st.session_state["images"]["player"])


def set_npc_image(npc_viz):
    for i, img in enumerate(st.session_state["images"]["characters"]):
        cont = npc_viz.container()
        cont.image(img)

def set_narration(words):
    for entry in st.session_state["narration"]:
        text = entry["text"]
        source = entry["source"]
        insert_text_content(words, text, source)

def main():
    set_layout()
    top_bar, content, bottom_bar = page_layout()
    player_viz, words, npc_viz = get_visual_content_dividers(content)
    left_buttons_area, text_inputs_area, right_buttons_area = player_input_area(bottom_bar)

    set_background_image()

    set_player_image(player_viz)
    set_npc_image(npc_viz)
    set_narration(words)
    
    player_input(text_inputs_area)


if __name__ == "__main__":
    main()