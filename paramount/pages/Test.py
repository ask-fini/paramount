import pandas as pd
import streamlit as st
from paramount.library_functions import (
    color_columns,
    format_func,
    large_centered_button,
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
        session = session.copy()  # to avoid SettingWithCopyWarning in our invocation of ast.literal_eval

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

        selected_input_var = st.selectbox("Select an input param to vary", session['session_input_cols'],
                                        format_func=format_func)

        if selected_input_var:
            most_common_input_content = session_df[selected_input_var].mode()
            first_mode_value = most_common_input_content.iloc[0] if not most_common_input_content.empty else None
            st.text_area("Most common value", first_mode_value)
            if large_centered_button("Test against ground truth"):
                st.write("Lol")

    # User selects input param, edits it, then clicks test - upon which a cosine distance is measured to ground truth

    # Challenge: How to replay in the UI - How to invoke the recorded function? Will need env vars from prod enviro?
    # Best way to do it is probably co-run (on diff port) with whichever production docker the user is using
    # Eg as an addition of "paramount *" on top of whichever pre-existing Docker run command (CMD exec)
else:
    st.write("No sessions found. Ensure you have recorded data, and that you have a saved ground truth session.")
