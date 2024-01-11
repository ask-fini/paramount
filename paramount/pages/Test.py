import pandas as pd
import streamlit as st
from paramount.library_functions import (
    color_columns,
    format_func,
    large_centered_button,
    hide_buttons,
)
import os
import ast
import requests
from dotenv import load_dotenv, find_dotenv


def get_values_dict(col_prefix, row):
    vals = {col.replace(col_prefix, ''): row[col] for col in row.index if col.startswith(col_prefix)}
    return vals


def clean_and_parse(val):
    try:
        return None if pd.isna(val) else ast.literal_eval(val)
    except (ValueError, SyntaxError, TypeError):
        return val


def invoke_via_api(func_name, base_url, args=None, kwargs=None):
    # construct the endpoint based on the function name
    endpoint = f'{base_url}/paramount/{func_name}'
    data_payload = {}
    if args is not None:
        data_payload['args'] = args
    if kwargs is not None:
        data_payload['kwargs'] = kwargs
    try:
        # Send the POST request to the endpoint with JSON payload
        response = requests.post(endpoint, json=data_payload)

        # Check if the request was successful
        if response.status_code == 200:
            # Handle successful response
            response = response.json()
        else:
            # Handle errors
            err = (response.status_code, response.text)
            print("Error:", err)
            response = err
    except requests.exceptions.RequestException as e:
        # Handle request exceptions (e.g., connection errors)
        print("Request failed:", e)
        response = e

    return response


hide_buttons()
st.title("Test tweaks and accuracy")
if find_dotenv():
    load_dotenv()
base_url = os.getenv('FUNCTION_API_BASE_URL')
filename = 'paramount_ground_truth_sessions.csv'

if 'clicked_eval' not in st.session_state:
    st.session_state.clicked_eval = False


def clicked():
    st.session_state.clicked_eval = True


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

        session_df = full_df[full_df['paramount__ground_truth'] == session['session_id']]

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
        to_update['paramount__ground_truth'] = None

        column_config.update(to_update)

        df = st.data_editor(data=color_columns(session_df), column_config=column_config, use_container_width=True,
                            disabled=disabled_cols, hide_index=True)

        selected_input_var = st.selectbox("Select an input param to vary", session['session_input_cols'],
                                          format_func=format_func)

        if selected_input_var:
            most_common_input_content = session_df[selected_input_var].mode()
            first_mode_value = most_common_input_content.iloc[0] if not most_common_input_content.empty else None
            edited_var = st.text_area("Most common value", first_mode_value)
            if edited_var:
                test_set = session_df.copy()
                test_set[selected_input_var] = edited_var
                large_centered_button("Test against ground truth", clicked)
                if st.session_state.clicked_eval:
                    clean_test_set = test_set.applymap(clean_and_parse)
                    session_output_cols = list(session['session_output_cols'])
                    progress_bar = st.progress(0, "Running against ground truth")
                    total_length = len(clean_test_set)
                    for i, (index, row) in enumerate(clean_test_set.iterrows()):
                        args = get_values_dict('input_args__', row)
                        kwargs = get_values_dict('input_kwargs__', row)
                        func_dict = {'args': args, 'kwargs': kwargs}

                        result = invoke_via_api(base_url=base_url, func_name=row['paramount__function_name'],
                                                args=args, kwargs=kwargs)
                        progress_bar.progress((i + 1) / total_length, "Running against ground truth")
                        for output_col in session_output_cols:
                            # Match function outputs to column names
                            identifying_info = output_col.split('__')[1].split('_')
                            output_index = int(identifying_info[0])-1
                            output_colname = None if len(identifying_info) < 2 else "_".join(identifying_info[1:])
                            data_item = result[output_index] if not output_colname else result[output_index][output_colname]
                            clean_test_set.at[index, 'test_'+output_col] = data_item

                    progress_bar.empty()
                    cols_to_display = session_output_cols + ['test_'+item for item in session_output_cols]

                    clean_test_set = clean_test_set[cols_to_display]
                    test_col_config = {col: format_func(col) for col in clean_test_set.columns}
                    clean_test_set['evaluation'] = None
                    test_col_config['evaluation'] = st.column_config.SelectboxColumn(
                        "Evaluation",
                        help="Evaluation of test run",
                        width="medium",
                        options=[
                            "✅ Accurate",
                            "❌ Inaccurate",
                        ],
                        required=True,
                    )

                    st.data_editor(data=color_columns(clean_test_set, False),
                                   column_config=test_col_config, use_container_width=True,
                                   disabled=cols_to_display, hide_index=True)

    # User selects input param, edits it, then clicks test - upon which a cosine distance is measured to ground truth

    # Challenge: How to replay in the UI - How to invoke the recorded function? Will need env vars from prod enviro?
    # Best way to do it is probably co-run (on diff port) with whichever production docker the user is using
    # Eg as an addition of "paramount *" on top of whichever pre-existing Docker run command (CMD exec)
else:
    st.write("No sessions found. Ensure you have recorded data, and that you have a saved ground truth session.")
