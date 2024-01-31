import pandas as pd
import streamlit as st
from paramount.library_functions import (
    color_columns,
    format_func,
    large_centered_button,
    hide_buttons,
    center_metric,
    db_connection,
    uuid_sidebar,
    validate_allowed,
)
import os
import ast
import requests
from dotenv import load_dotenv, find_dotenv
if find_dotenv():
    load_dotenv()
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
st.set_page_config(layout="wide", page_title="Fini Paramount - Business Evals")
db_instance = db_connection()
uuid_sidebar()
paramount_identifier_colname = os.getenv('PARAMOUNT_IDENTIFIER_COLNAME')
PARAMOUNT_OUTPUT_COLS = ast.literal_eval(os.getenv('PARAMOUNT_OUTPUT_COLS'))


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


def run():
    hide_buttons()
    if not validate_allowed():
        return
    st.title("Optimize performance with tweaks")
    if find_dotenv():
        load_dotenv()
    base_url = os.getenv('FUNCTION_API_BASE_URL')

    inits = ['clicked_eval']
    for var in inits:
        if var not in st.session_state:
            st.session_state[var] = False

    def clicked(var, value):
        st.session_state[var] = value

    ground_truth_table_name = 'paramount_data'

    if db_instance.table_exists(ground_truth_table_name):
        read_df = db_instance.get_table(ground_truth_table_name, random_sample=False,
                                        identifier_value=st.session_state['user_identifier'],
                                        identifier_column_name=paramount_identifier_colname)

        input_params = [col for col in read_df.columns if col.startswith('input_')]
        selected_input_var = st.selectbox("Select an input param to vary", input_params,
                                          format_func=format_func)

        if selected_input_var:
            most_common_input_content = read_df[selected_input_var].mode()
            first_mode_value = most_common_input_content.iloc[0] if not most_common_input_content.empty else None
            edited_var = st.text_area("Most common value", first_mode_value)
            if edited_var:
                test_set = read_df.copy()
                test_set[selected_input_var] = edited_var

                output_params = [col for col in read_df.columns if col.startswith('output__')]

                selected_output_var = st.selectbox(
                    "Select an output param to measure similarity: ground truth <> test set",
                    output_params, format_func=format_func)

                large_centered_button("Test against ground truth", clicked, args=('clicked_eval', True))
                if st.session_state['clicked_eval'] and selected_output_var:
                    session_output_cols = ['output__' + col for col in PARAMOUNT_OUTPUT_COLS]
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

                            result = invoke_via_api(base_url=base_url, func_name=row['paramount__function_name'],
                                                    args=args, kwargs=kwargs)
                            progress_bar.progress((i + 1) / total_length, "Running against ground truth")
                            for output_col in session_output_cols:
                                # Match function outputs to column names
                                identifying_info = output_col.split('__')[1].split('_')
                                output_index = int(identifying_info[0])-1
                                output_colname = None if len(identifying_info) < 2 else\
                                    "_".join(identifying_info[1:])
                                data_item = result[output_index] if not output_colname else\
                                    result[output_index][output_colname]
                                clean_test_set.at[index, 'test_'+output_col] = str(data_item)

                        progress_bar.empty()
                        clean_test_set = clean_test_set[cols_to_display]

                        vectorizer = TfidfVectorizer()

                        # To ensure comparability
                        clean_test_set[selected_output_var] = clean_test_set[selected_output_var].astype(str)
                        clean_test_set['test_' + selected_output_var] =\
                            clean_test_set['test_' + selected_output_var].astype(str)

                        tfidf_matrix = vectorizer.fit_transform(clean_test_set[selected_output_var])

                        # Transform both the ground truth and test set data (columns 1 and 2)
                        tfidf_matrix_ground_truth = vectorizer.transform(clean_test_set[selected_output_var])
                        tfidf_matrix_test_set = vectorizer.transform(clean_test_set['test_'+selected_output_var])

                        # Calculate cosine similarity between the corresponding rows in columns 1 and 2
                        cosine_similarities = [cosine_similarity(tfidf_matrix_ground_truth[i:i + 1],
                                                                 tfidf_matrix_test_set[i:i + 1])[0][0]
                                               for i in range(tfidf_matrix_ground_truth.shape[0])]

                        # Add the cosine similarity scores to the DataFrame
                        clean_test_set['cosine_similarity'] = cosine_similarities
                        clean_test_set['cosine_similarity'] *= 100  # For percent display

                    test_col_config = {col: format_func(col) for col in clean_test_set.columns}
                    test_col_config['cosine_similarity'] = st.column_config.ProgressColumn(
                        "Similarity",
                        help="Cosine similarity versus ground truth",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    )

                    st.data_editor(data=color_columns(clean_test_set, False),
                                   column_config=test_col_config, use_container_width=True, on_change=clicked,
                                   args=('clean_test_set', clean_test_set), disabled=cols_to_display,
                                   hide_index=True)

                    average_similarity = clean_test_set['cosine_similarity'].mean()
                    formatted_average_similarity = "{:.2f}%".format(average_similarity)
                    center_metric()
                    st.metric(label="Average similarity to evaluation", value=formatted_average_similarity)
                    st.session_state['clicked_eval'] = False
    else:
        st.write("No evaluations found. Ensure you have recorded data, and that you have saved some evaluations.")


if __name__ == '__main__':
    run()
