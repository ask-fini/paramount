import streamlit as st
import pandas as pd
from db_connector import db
import uuid


@st.cache_resource
def db_connection():
    db_instance = db.get_database()
    return db_instance


def large_centered_button(text, on_click=None, args=None):
    st.markdown("<style> .stButton>button { height: 3em; width: 20em; } </style>", unsafe_allow_html=True)
    st.markdown("<style>div.row-widget.stButton { display: flex; justify-content: center; }</style>",
                unsafe_allow_html=True)
    return st.button(text, on_click=on_click, args=args)


def get_result_from_colname(result, output_col):
    '''
    Match function outputs to column names.
    For example, This turns 'output__1_answer' into -> (1, answer)
    Where 1 is the index to use of the returned tuple, and answer is the output varname (if exists)
    :param result:
    :param output_col:
    :return:
    '''
    identifying_info = output_col.split('__')[1].split('_')  # output__1_answer -> [1, answer]
    output_index = int(identifying_info[0]) - 1  # 1 -> 0th index
    output_colname = None if len(identifying_info) < 2 else "_".join(identifying_info[1:])  # answer or blank if no name
    data_item = result[output_index] if not output_colname else result[output_index][output_colname]  # Get the value
    return output_index, output_colname, data_item


def uuid_sidebar():
    def change_default(cid):
        for item in st.session_state:  # Reset the state of the pages, as a cleanup now that identifier is changed
            st.session_state.pop(item, None)

        st.session_state['user_identifier'] = cid

    user_identifier = ""
    if 'user_identifier' in st.session_state:
        user_identifier = st.session_state['user_identifier']

    user_identifier = st.sidebar.text_input("Enter Identifier", value=user_identifier, on_change=change_default,
                                         args=(user_identifier,))

    if 'user_identifier' in st.session_state:
        st.session_state['user_identifier'] = user_identifier


def is_valid_uuidv4(uuid_to_test):
    try:
        # Try converting string to UUID object
        uuid_obj = uuid.UUID(uuid_to_test, version=4)

        # Check if generated UUID matches the supplied string
        # and that the version is 4
        return str(uuid_obj) == uuid_to_test and uuid_obj.version == 4
    except (ValueError, AttributeError, TypeError):
        return False


def validate_allowed():
    allowed = False
    if 'user_identifier' in st.session_state and is_valid_uuidv4(st.session_state['user_identifier']):
        allowed = True
    else:
        st.write("Please enter a correct identifier to access the service")
    return allowed


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