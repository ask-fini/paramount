import pandas as pd
import streamlit as st
from paramount.library_functions import (
    color_columns,
    format_func,
    large_centered_button,
    hide_buttons,
    center_metric,
)
import os
import ast
import requests
from dotenv import load_dotenv, find_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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
    endpoint = f'{base_url}/paramount_functions/{func_name}'
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

inits = ['clicked_eval']
for var in inits:
    if var not in st.session_state:
        st.session_state[var] = False


def clicked(var, value):
    st.session_state[var] = value


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

        # TODO: These two operations may be very inefficient for large amount of rows?
        full_df['paramount__ground_truth'] = full_df['paramount__ground_truth'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) and x.strip().startswith('[') and x.strip().endswith(
                ']') else [])
        session_df = full_df[full_df['paramount__ground_truth'].apply(lambda ids: session['session_id'] in ids)]

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

                selected_output_var = st.selectbox(
                    "Select an output param to measure similarity: ground truth <> test set",
                    session['session_output_cols'], format_func=format_func)

                large_centered_button("Test against ground truth", clicked, args=('clicked_eval', True))
                if st.session_state['clicked_eval'] and selected_output_var:
                    session_output_cols = list(session['session_output_cols'])
                    cols_to_display = session_output_cols + ['test_' + item for item in session_output_cols]

                    # Now decide what DataFrame to use for the data_editor based on session state
                    if 'clean_test_set' in st.session_state:
                        clean_test_set = st.session_state['clean_test_set']
                    else:
                        clean_test_set = test_set.applymap(clean_and_parse)
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
                        clean_test_set = clean_test_set[cols_to_display]

                        vectorizer = TfidfVectorizer()
                        tfidf_matrix = vectorizer.fit_transform(clean_test_set[selected_output_var])

                        # Transform both the ground truth and test set data (columns 1 and 2)
                        tfidf_matrix_ground_truth = vectorizer.transform(clean_test_set[selected_output_var])
                        tfidf_matrix_test_set = vectorizer.transform(clean_test_set['test_'+selected_output_var])

                        # Calculate cosine similarity between the corresponding rows in columns 1 and 2
                        cosine_similarities = [cosine_similarity(tfidf_matrix_ground_truth[i:i + 1], tfidf_matrix_test_set[i:i + 1])[0][0]
                                               for i in range(tfidf_matrix_ground_truth.shape[0])]

                        # Add the cosine similarity scores to the DataFrame
                        clean_test_set['cosine_similarity'] = cosine_similarities
                        clean_test_set['cosine_similarity'] *= 100  # For percent display

                    test_col_config = {col: format_func(col) for col in clean_test_set.columns}
                    clean_test_set['evaluation'] = None
                    test_col_config['evaluation'] = st.column_config.SelectboxColumn(
                        "Evaluation",
                        help="Evaluation of test run",
                        width="medium",
                        options=[
                            "✅ Accurate",
                            "❔ Missing Info",  # RAG failed or Document missing
                            "❌ Irrelevant Extra Info",  # RAG failed, included too much
                            "🕰️ Wrong/Outdated Info",  # Document needs updating
                            "📃 Didn't follow instruction"  # Prompt was wrong
                        ],
                        required=True,
                    )

                    test_col_config['cosine_similarity'] = st.column_config.ProgressColumn(
                        "Similarity",
                        help="Cosine similarity versus ground truth",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    )

                    st.data_editor(data=color_columns(clean_test_set, False),
                                   column_config=test_col_config, use_container_width=True, on_change=clicked,
                                   args=('clean_test_set', clean_test_set), disabled=cols_to_display, hide_index=True)

                    average_similarity = clean_test_set['cosine_similarity'].mean()
                    formatted_average_similarity = "{:.2f}%".format(average_similarity)
                    center_metric()
                    st.metric(label="Average similarity", value=formatted_average_similarity)

                    st.session_state['clicked_eval'] = False

    # LATER
    # Fix Large nr of rows TODO
    # LLM similarity
    # Evaluation pre-fill
    # Save to postgres. One table per function? then "function name" col is redundant

else:
    st.write("No sessions found. Ensure you have recorded data, and that you have a saved ground truth session.")
