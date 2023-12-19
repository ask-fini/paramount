import streamlit as st


def hide_buttons():
    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {
                display: none;
            }
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)