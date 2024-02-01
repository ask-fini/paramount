import pandas as pd
import streamlit as st
import ast
import os
import pytz
from datetime import datetime
from paramount.library_functions import (
    hide_buttons,
    color_columns,
    get_colors,
    format_func,
    large_centered_button,
    db_connection,
    uuid_sidebar,
    validate_allowed,
    center_metric,
)
from dotenv import load_dotenv, find_dotenv
if find_dotenv():
    load_dotenv()
st.set_page_config(layout="wide", page_title="Fini Paramount - Business Evals")
db_instance = db_connection()
uuid_sidebar()
paramount_identifier_colname = os.getenv('PARAMOUNT_IDENTIFIER_COLNAME')
PARAMOUNT_META_COLS = ast.literal_eval(os.getenv('PARAMOUNT_META_COLS'))
PARAMOUNT_INPUT_COLS = ast.literal_eval(os.getenv('PARAMOUNT_INPUT_COLS'))
PARAMOUNT_OUTPUT_COLS = ast.literal_eval(os.getenv('PARAMOUNT_OUTPUT_COLS'))
eval_col = 'paramount__evaluation'
accurate_eval = '✅ Accurate'


def run():
    hide_buttons()
    if not validate_allowed():
        return

    st.title('Evaluate responses')
    st.write('Based on the 100 latest entries')
    ground_truth_table_name = 'paramount_data'

    if db_instance.table_exists(ground_truth_table_name):
        read_df = db_instance.get_table(ground_truth_table_name, all_rows=True,
                                        identifier_value=st.session_state['user_identifier'],
                                        identifier_column_name=paramount_identifier_colname)
        possible_cols = read_df.columns

        read_df[eval_col] = read_df[eval_col].fillna('')

        input_cols = [col for col in possible_cols if col.startswith("input_")]
        output_cols = [col for col in possible_cols if col.startswith("output_")]

        paramount_suffix = ['recording_id', 'timestamp', 'function_name', 'execution_time']
        paramount_cols = ['paramount__' + suffix for suffix in paramount_suffix]

        col_mapping = {'paramount__': paramount_cols, 'input_args__': input_cols,
                       'input_kwargs__': input_cols, 'output__': output_cols}

        # Generate CSS selectors and rules
        css_rules = []
        for prefix, cols in col_mapping.items():
            color = get_colors().get(prefix)
            selectors = [f'[aria-label^="{col.replace(prefix, "")}"]' for col in cols]
            selector_str = ", ".join(selectors)
            rule = f"{selector_str} {{ background-color: {color}; color: black; }}"
            css_rules.append(rule)

        # Combine all rules and pass to st.markdown
        css_code = "\n".join(css_rules)
        st.markdown(f"<style>{css_code}</style>", unsafe_allow_html=True)

        selected_id_cols = ['paramount__' + col for col in PARAMOUNT_META_COLS]
        selected_input_cols = ['input_' + col for col in PARAMOUNT_INPUT_COLS]
        selected_output_cols = ['output__' + col for col in PARAMOUNT_OUTPUT_COLS]

        filtered_cols = [eval_col] + selected_id_cols + selected_input_cols + selected_output_cols
        filtered_cols = list(dict.fromkeys(filtered_cols))  # Avoids column name duplication but maintains order

        # Now decide what DataFrame to use for the data_editor based on session state
        if 'full_df' in st.session_state:
            full_df = st.session_state['full_df']
        else:
            full_df = read_df.reset_index(drop=True)

        disabled_cols = set([col for col in full_df.columns if col not in [eval_col] + selected_output_cols])

        column_config = {col: format_func(col) for col in full_df.columns}
        column_config.update({column: None for column in possible_cols if column not in filtered_cols})
        full_df[eval_col] = full_df[eval_col].astype(str)
        column_config[eval_col] = st.column_config.SelectboxColumn(
            "Evaluation",
            width="medium",
            options=[
                accurate_eval,
                "❔ Missing Info",  # RAG failed or Document missing
                "❌ Irrelevant Extra Info",  # RAG failed, included too much
                "🕰️ Wrong/Outdated Info",  # Document needs updating
                "📃 Didn't follow instruction",  # Prompt was wrong
            ],
            required=False
        )

        def on_change(full_df):  # Needed to ensure UI updates are synchronized correctly across ground truth clicks
            st.session_state['full_df'] = full_df

        full_df = st.data_editor(data=color_columns(full_df), column_config=column_config,
                                 use_container_width=True, disabled=disabled_cols, hide_index=True,
                                 on_change=on_change, args=(full_df,))

        # Update evaluated_at column wherever evaluations have been made (detected via != versus original df)
        diff_eval_ids = read_df.index[read_df[eval_col] != full_df.loc[read_df.index, eval_col]]
        current_time_utc = datetime.now(pytz.timezone('UTC')).replace(microsecond=0).isoformat()
        full_df.loc[diff_eval_ids, 'paramount__evaluated_at'] = current_time_utc
        full_df[eval_col] = full_df[eval_col].fillna('').astype(str)

        if len(full_df) > 0:
            accuracy = 100*len(full_df[full_df[eval_col] == accurate_eval]) / len(full_df)
            formatted_accuracy = "{:.1f}%".format(accuracy)
            center_metric()
            st.metric(label="Accuracy", value=formatted_accuracy)
            if large_centered_button("Save session"):
                # Including selected_output_cols in the merge, in order to include any UI edits done for the outputs
                merged = pd.merge(full_df[[eval_col, 'paramount__recording_id', 'paramount__evaluated_at']+selected_output_cols],
                                  read_df.drop(columns=[eval_col, 'paramount__evaluated_at']+selected_output_cols,
                                               errors='ignore'), on='paramount__recording_id', how='right')

                db_instance.update_ground_truth(merged, ground_truth_table_name)

                st.session_state['full_df'] = full_df
                st.rerun()

    else:
        st.write("No data found. Ensure you use @paramount.record decorator on any functions you want to record.")


if __name__ == '__main__':
    run()
