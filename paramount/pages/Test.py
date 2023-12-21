import pandas as pd
import streamlit as st
from paramount.library_functions import (
    hide_buttons,
    color_columns,
    get_colors,
    format_func,
)
import os
import ast

# hide_buttons()
st.title("Test tweaks and accuracy")

filename = 'paramount_ground_truth_sessions.csv'
if os.path.isfile(filename):

    sessions = pd.read_csv('paramount_ground_truth_sessions.csv')
    sessions['session_time'] = pd.to_datetime(sessions['session_time'])
    timestr = sessions.sort_values('session_time')['session_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    namestr = sessions.sort_values('session_time')['session_name']
    available_sessions = timestr + ': ' + namestr

    session_to_index = pd.Series(sessions.sort_values('session_time').index, index=available_sessions)

    # User selects a session from Streamlit's selectbox
    selected_session = st.selectbox("Select a ground truth session", available_sessions)

    if selected_session:
        # Retrieve the index of the selected session
        session_index = session_to_index[selected_session]
        # Retrieve the full row corresponding to the selected session
        session = sessions.loc[session_index]

        filename = 'paramount_data.csv'
        full_df = pd.read_csv(filename)

        session_df = full_df[full_df['paramount_ground_truth'] == session['session_id']]

        editable_columns = []

        filtered_cols = session['session_all_filtered_cols']

        colnames_cols = ['session_id_cols', 'session_input_cols', 'session_output_cols', 'session_all_filtered_cols',
                         'session_all_possible_cols']

        # Convert the column lists from strings back to their actual list format
        for df_column_list in colnames_cols:
            session[df_column_list] = ast.literal_eval(session[df_column_list])

        disabled_cols = set([col for col in full_df.columns if col not in editable_columns])
        column_config = {col: format_func(col) for col in session_df.columns}
        to_update = {column: None for column in session['session_all_possible_cols'] if column not in filtered_cols}
        to_update['paramount_ground_truth'] = None

        column_config.update(to_update)

        df = st.data_editor(data=color_columns(session_df), column_config=column_config, use_container_width=True,
                            disabled=disabled_cols, hide_index=True)

    # TODO: Test mode: load in the ground truth table belonging to a session ID
    # User selects "param to vary", and specifies a new value to test with. then clicks "Test" button
    # Also accuracy measurement function choice will have to be made eg cosine distance
    # Challenge: How to replay in the UI - How to invoke the recorded function? Will need env vars from prod enviro?
    # Best way to do it is probably co-run (on diff port) with whichever production docker the user is using
    # Eg as an addition of "paramount *" on top of whichever pre-existing Docker run command (CMD exec)
else:
    st.write("No sessions found. Ensure you have recorded data, and that you have a saved ground truth session.")
