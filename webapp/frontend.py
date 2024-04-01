import streamlit as st

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

def top_navigation(top_bar, button_names: list[str], button_funcs: list[callable]):
    assert len(button_names) == len(button_funcs)
    n_buttons = len(button_names)
    cols = top_bar.columns(n_buttons)
    for idx in range(n_buttons):
        cols[idx].button(button_names[idx], key=f"top_button_{idx}", use_container_width=True)
    for idx in range(n_buttons):
        if st.session_state[f"top_button_{idx}"]:
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
