import streamlit as st
from importlib.resources import read_text
import random


@st.cache_data
def get_words():
    word_file = read_text('paramount', 'thousand_random_words.txt')
    word_list = word_file.splitlines()
    return word_list


def random_suggested_name():
    return ' '.join([item[0].upper() + item[1:].lower() for item in random.sample(get_words(), 2)])


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