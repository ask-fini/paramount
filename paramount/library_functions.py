import streamlit as st
from importlib.resources import read_text
import random
import pandas as pd
from .db_connector import db


@st.cache_data
def get_words():
    word_file = read_text('paramount', 'thousand_random_words.txt')
    word_list = word_file.splitlines()
    return word_list


@st.cache_resource
def db_connection():
    db_instance = db.get_database()
    return db_instance


def large_centered_button(text, on_click=None, args=None):
    st.markdown("<style> .stButton>button { height: 3em; width: 20em; } </style>", unsafe_allow_html=True)
    st.markdown("<style>div.row-widget.stButton { display: flex; justify-content: center; }</style>",
                unsafe_allow_html=True)
    return st.button(text, on_click=on_click, args=args)


def center_metric():
    css = '''
    [data-testid="stMetric"] {
        width: fit-content;
        margin: auto;
    }

    [data-testid="stMetric"] > div {
        width: fit-content;
        margin: auto;
    }

    [data-testid="stMetric"] label {
        width: fit-content;
        margin: auto;
    }
    '''

    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


def random_suggested_name():
    return ' '.join([item[0].upper() + item[1:].lower() for item in random.sample(get_words(), 2)])


def get_colors():
    colors = {
        'paramount__': '#ACCBE1',  # Soft blue
        'input_args__': '#C2E0C6',  # Pale green
        'input_kwargs__': '#C2E0C6',  # Pale green
        'output__': '#FFF2CC',  # Light yellow
    }
    return colors


def test_colors():
    colors = {
        'test_output__': '#E6E6FA',  # Lavender (Light Purple)
        'output__': '#D3D3D3',  # Light Gray
    }
    return colors


def format_func(col):
    return col.split("__")[1] if "__" in col else col


def color_columns(df: pd.DataFrame, regular_colors=True):
    # Create a color map based on column prefixes
    color_scheme = get_colors if regular_colors else test_colors
    color_map = {col: f'background-color: {color}' for prefix, color in
                 color_scheme().items() for col in df.columns if col.startswith(prefix)}

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