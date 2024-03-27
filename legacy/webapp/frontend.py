import streamlit as st


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