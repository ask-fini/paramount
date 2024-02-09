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
    get_result_from_colname,
)
import os
import ast
import requests
from dotenv import load_dotenv, find_dotenv
if find_dotenv():
    load_dotenv()
st.set_page_config(layout="wide", page_title="Fini Paramount - Business Evals")
db_instance = db_connection()
uuid_sidebar()
paramount_identifier_colname = os.getenv('PARAMOUNT_IDENTIFIER_COLNAME')
PARAMOUNT_OUTPUT_COLS = ast.literal_eval(os.getenv('PARAMOUNT_OUTPUT_COLS'))
PARAMOUNT_API_ENDPOINT = os.getenv('PARAMOUNT_API_ENDPOINT')


def clean_and_parse(val):
    try:
        return None if pd.isna(val) else ast.literal_eval(val)
    except (ValueError, SyntaxError, TypeError):
        return val


def run():
    hide_buttons()
    if not validate_allowed():
        return
    st.title("Optimize performance with tweaks")
    if find_dotenv():
        load_dotenv()

    inits = ['clicked_eval']
    for var in inits:
        if var not in st.session_state:
            st.session_state[var] = False

    def clicked(var, value):
        st.session_state[var] = value

    results = requests.post(f'{PARAMOUNT_API_ENDPOINT}/latest',
                            json={'evaluated_rows_only': True, 'company_uuid': st.session_state['user_identifier']})
    if results.status_code == 200:
        records = results.json().get('result', [])
        column_order = results.json().get('column_order', [])
        read_df = pd.DataFrame(records)[column_order]

        column_config = {col: format_func(col) for col in read_df.columns}
        st.dataframe(data=color_columns(read_df), column_config=column_config, use_container_width=True, hide_index=True)

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
                        progress_bar = st.progress(0, "Running against evaluation")
                        total_length = len(clean_test_set)
                        for i, (index, row) in enumerate(clean_test_set.iterrows()):
                            record = row.to_dict()
                            result = requests.post(f'{PARAMOUNT_API_ENDPOINT}/infer',
                                                   json={'record': record, 'output_cols': session_output_cols})
                            result = result.json().get('result', {})
                            for output_col in session_output_cols:
                                _, _, data_item = get_result_from_colname(result, output_col)
                                clean_test_set.at[index, 'test_' + output_col] = str(data_item)
                            evalstr = f"Running against evaluation {i+1}/{total_length}"
                            progress_bar.progress((i + 1) / total_length, evalstr)

                        progress_bar.empty()
                        clean_test_set = clean_test_set[cols_to_display]

                        result = requests.post(f'{PARAMOUNT_API_ENDPOINT}/similarity',
                                               json={'output_col_to_be_tested': selected_output_var,
                                                     'records': clean_test_set.to_dict(orient='records')})
                        cosine_similarities = result.json().get('result', {})

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
