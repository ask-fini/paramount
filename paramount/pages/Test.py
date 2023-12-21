import pandas as pd
import streamlit as st
from paramount.library_functions import hide_buttons
import os

hide_buttons()
st.title("Test tweaks and accuracy")

filename = 'paramount_ground_truth_sessions.csv'
if os.path.isfile(filename):

    sessions = pd.read_csv('paramount_ground_truth_sessions.csv')
    sessions['session_time'] = pd.to_datetime(sessions['session_time'])
    available_sessions = sessions['session_name'] + sessions['session_time'].dt.strftime(' - %Y-%m-%d %H:%M:%S')

    # Create a mapping from the available_sessions to session_id
    session_to_id = dict(zip(available_sessions, sessions['session_id']))

    # Select a session using the selectbox
    selected_session = st.selectbox("Select a ground truth session", available_sessions)

    if selected_session:
        # Retrieve the session_id using the selected session name and time
        session_id = session_to_id[selected_session]

        # Now load the specific DataFrame for the selected session_id from the merged CSV file
        filename = 'paramount_data.csv'
        full_df = pd.read_csv(filename)

        # Filter the full_df by the selected session_id
        session_df = full_df[full_df['paramount_ground_truth'] == session_id]

        # Display the DataFrame for the selected session
        st.dataframe(session_df)

    # TODO: Test mode: load in the ground truth table belonging to a session ID
    # User selects "param to vary", and specifies a new value to test with. then clicks "Test" button
    # Also accuracy measurement function choice will have to be made eg cosine distance
    # Challenge: How to replay in the UI - How to invoke the recorded function? Will need env vars from prod enviro?
    # Best way to do it is probably co-run (on diff port) with whichever production docker the user is using
    # Eg as an addition of "paramount *" on top of whichever pre-existing Docker run command (CMD exec)
else:
    st.write("No sessions found. Ensure you have recorded data, and that you have a saved ground truth session.")
