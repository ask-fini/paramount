import pandas as pd
import streamlit as st
from paramount.library_functions import hide_buttons
from glob import glob

hide_buttons()
st.title("Select a ground truth session to test against")
sessions = pd.read_csv('paramount_ground_truth_sessions.csv')
st.data_editor(sessions)


# TODO: Test mode: load in the ground truth table belonging to a session ID
# User selects "param to vary", and specifies a new value to test with. then clicks "Test" button
# Also accuracy measurement function choice will have to be made eg cosine distance
# Challenge: How to replay in the UI - How to invoke the recorded function? Will need env vars from prod enviro?
# Best way to do it is probably co-run (on diff port) with whichever production docker the user is using
# Eg as an addition of "paramount *" on top of whichever pre-existing Docker run command (CMD exec)
