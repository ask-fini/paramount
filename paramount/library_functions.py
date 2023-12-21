import streamlit as st
from importlib.resources import read_text
import random
import pandas as pd


@st.cache_data
def get_words():
    word_file = read_text('paramount', 'thousand_random_words.txt')
    word_list = word_file.splitlines()
    return word_list


def random_suggested_name():
    return ' '.join([item[0].upper() + item[1:].lower() for item in random.sample(get_words(), 2)])


def get_colors():
    colors = {
        'paramount_': '#ACCBE1',  # Soft blue
        'input_': '#C2E0C6',  # Pale green
        'output_': '#FFF2CC',  # Light yellow
    }
    return colors


def format_func(col):
    return "_".join(col.split("_")[1:]) if "_" in col else col


def color_columns(df: pd.DataFrame):
    # Create a color map based on column prefixes
    color_map = {col: f'background-color: {color}' for prefix, color in
                 get_colors().items() for col in df.columns if col.startswith(prefix)}

    # Styling function to apply color_map
    styler = df.style.apply(lambda x: [color_map.get(x.name, '') for _ in x], axis=0)

    # Return the styler to display the DataFrame with the colored columns
    return styler


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