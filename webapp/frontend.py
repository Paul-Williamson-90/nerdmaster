import streamlit as st
import numpy as np

def page_layout():
    page = st.container(bordered=True)
    top_bar = page.container(bordered=True)
    content = page.container(bordered=True)
    bottom_bar = page.container(bordered=True)
    return top_bar, content, bottom_bar

def get_visual_content_dividers(content):
    (player_viz,
     words,
     npc_viz) = content.columns(3, bordered=True)
    return player_viz, words, npc_viz

def get_item_mode_dividers(words):
    left_item_menu, right_item_menu = words.columns(2, bordered=True)
    return left_item_menu, right_item_menu

def insert_text_content(words, text, source):
    text_entry = words.container(bordered=False)
    player, narrator, npc = text_entry.columns(3, bordered=False)
    source_idx = ["player", "narrator", "npc"].index(source)
    col = [player, narrator, npc][source_idx]
    alignment = ["left", "center", "right"][source_idx]
    bubble = col.container(bordered=True)
    bubble.write(text)

def player_input_area(bottom_bar):
    left_buttons_area, text_inputs_area, right_buttons_area = bottom_bar.columns(3, bordered=True)
    return left_buttons_area, text_inputs_area, right_buttons_area

def top_navigation(
    top_bar, 
    button_names: list[str], 
    button_funcs: list[callable]
):
    assert len(button_names) == len(button_funcs)
    n_buttons = len(button_names)
    cols = top_bar.columns(n_buttons)
    for idx in range(n_buttons):
        cols[idx].button(button_names[idx], key=f"top_button_{idx}", use_container_width=True)
    for idx in range(n_buttons):
        if st.session_state[f"top_button_{idx}"]:
            button_funcs[idx]()

def page_structure_by_mode(
    mode, 
    button_names: list[str], 
    button_funcs: list[callable]
):
    top_bar, content, bottom_bar = page_layout()
    top_navigation(top_bar, button_names, button_funcs)
    left_buttons_area, text_inputs_area, right_buttons_area = player_input_area(bottom_bar)
    if mode in ["dialogue", "combat", "explore"]:
        player_viz, words, npc_viz = get_visual_content_dividers(content)
        return (
            left_buttons_area, 
            text_inputs_area, 
            right_buttons_area,
            player_viz, 
            words, 
            npc_viz
        )
    elif mode in ["trade"]:
        player_viz, words, npc_viz = get_visual_content_dividers(content)
        left_item_menu, right_item_menu = get_item_mode_dividers(words)
        return (
            player_viz, 
            npc_viz,
            left_item_menu, 
            right_item_menu
        )
    else:
        raise TypeError("Game mode not recognised")

def add_text_to_content(
    words, 
    text_inputs: list[dict[str, str]], 
    msg_limit: int = 5)
:
    for text in text_inputs[-msg_limit:]:
        insert_text_content(words, text["text"], text["source"])

def side_buttons(
    container, 
    button_names: list[str], 
    button_funcs: list[callable],
    key_tag: str = "left"
):
    assert len(button_names) == len(button_funcs)
    n = len(button_names)
    n_cols, n_rows = np.ceiling(np.sqrt(n))
    starts = [x for x in range(0, n_cols*n_rows, n_rows)]
    for i in starts:
        row = container.container()
        cells = row.columns(n_cols, bordered=True)
        for k in range(n_cols):
            idx = i+k
            cells[k].button(button_names[idx], key=f"{key_tag}_{idx}")
    
    for i in starts:
        for k in range(n_cols):
            idx = i+k
            if st.session_state[f"{key_tag}_{idx}"]:
                button_funcs[idx]()
            
            

def set_layout():
    st.set_page_config(initial_sidebar_state="collapsed", 
                    #    layout="wide"
                       )

    st.markdown(
        """
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def main():
    set_layout()
    st.switch_page("pages/setup_game.py")


if __name__ == "__main__":
    main()
