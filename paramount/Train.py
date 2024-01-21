import pandas as pd
import streamlit as st
import uuid
import pytz
import ast
import os
from datetime import datetime
from paramount.library_functions import (
    hide_buttons,
    random_suggested_name,
    color_columns,
    get_colors,
    format_func,
    large_centered_button,
    db_connection,
    uuid_sidebar,
    validate_allowed,
)
from dotenv import load_dotenv, find_dotenv
if find_dotenv():
    load_dotenv()
st.set_page_config(layout="wide", page_title="Fini Paramount - Agent-Centric Evals")
db_instance = db_connection()
uuid_sidebar()
paramount_identifier_colname = os.getenv('PARAMOUNT_IDENTIFIER_COLNAME')


def run():
    hide_buttons()
    if not validate_allowed():
        return

    st.title('Record ground truth data')
    ground_truth_table_name = 'paramount_data'

    if db_instance.table_exists(ground_truth_table_name):
        read_df = db_instance.get_table(ground_truth_table_name, records_data=True,
                                        identifier_value=st.session_state['user_identifier'],
                                        identifier_column_name=paramount_identifier_colname)
        possible_cols = read_df.columns

        input_cols = [col for col in possible_cols if col.startswith("input_")]
        output_cols = [col for col in possible_cols if col.startswith("output_")]

        paramount_suffix = ['recording_id', 'timestamp', 'function_name', 'execution_time']
        paramount_cols = ['paramount__' + suffix for suffix in paramount_suffix]
        identifier_cols = paramount_cols + input_cols

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

        selected_id_cols = st.multiselect('Identifier and info columns', identifier_cols, format_func=format_func)
        selected_input_cols = st.multiselect('Input columns', input_cols, format_func=format_func)
        selected_output_cols = st.multiselect('Output columns', output_cols, format_func=format_func)

        if not selected_id_cols and not selected_input_cols and not selected_output_cols:
            filtered_cols = possible_cols
            selection_made = False
        else:
            filtered_cols = ['paramount__ground_truth'] + selected_id_cols + selected_input_cols + selected_output_cols
            filtered_cols = list(dict.fromkeys(filtered_cols))  # Avoids column name duplication but maintains order
            selection_made = True

        # Now decide what DataFrame to use for the data_editor based on session state
        if 'full_df' in st.session_state:
            full_df = st.session_state['full_df']
        else:
            full_df = read_df.reset_index(drop=True)
            # Turn session_id into a checkbox in the UI
            full_df['paramount__ground_truth'] = full_df['paramount__ground_truth'].apply(
                lambda x: [] if pd.isna(x) else
                (ast.literal_eval(x) if isinstance(x, str) and x.strip().startswith("[") else [x]))
            full_df.insert(0, 'paramount__ground_truth_boolean',  # insert at 0 makes it the first column
                           full_df['paramount__ground_truth'].apply(lambda x: bool(x)))

        disabled_cols = set([col for col in full_df.columns if col not in ["paramount__ground_truth_boolean"] + selected_output_cols])

        column_config = {col: format_func(col) for col in full_df.columns}
        column_config['paramount__ground_truth_boolean'] = 'Ground Truth?'
        column_config['paramount__ground_truth'] = None  # Hides the column

        if selection_made:  # Updates the config for unselected cols to hide them
            column_config.update({column: None for column in possible_cols if column not in filtered_cols})

        def on_change(full_df):  # Needed to ensure UI updates are synchronized correctly across ground truth clicks
            st.session_state['full_df'] = full_df

        full_df = st.data_editor(data=color_columns(full_df), column_config=column_config,
                                 use_container_width=True, disabled=disabled_cols, hide_index=True,
                                 on_change=on_change, args=(full_df,))

        if 'random_suggested_name' not in st.session_state:
            st.session_state['random_suggested_name'] = random_suggested_name()

        session_name = st.text_input("Session name (optional)", value=st.session_state['random_suggested_name'])
        if selection_made and len(full_df) > 0:
            if large_centered_button("Save session"):
                session_id = str(uuid.uuid4())
                session_df = {
                    'session_id': session_id,
                    'session_name': session_name,
                    'session_time': datetime.now(pytz.timezone('UTC')).replace(microsecond=0).isoformat(),
                    'session_id_cols': list(selected_id_cols),
                    'session_input_cols': list(selected_input_cols),
                    'session_output_cols': list(selected_output_cols),
                    'session_all_filtered_cols': list(filtered_cols),
                    'session_all_possible_cols': list(possible_cols),
                    'session_user_identifier': st.session_state['user_identifier'],
                }

                # Including selected_output_cols in the merge, in order to include any UI edits done for the outputs
                merged = pd.merge(full_df[['paramount__ground_truth', 'paramount__ground_truth_boolean',
                                           'paramount__recording_id']+selected_output_cols],
                                  read_df.drop(columns=['paramount__ground_truth']+selected_output_cols,
                                               errors='ignore'), on='paramount__recording_id', how='right')

                # To not mess up the order of output cols
                merged = merged.reindex(columns=['paramount__ground_truth_boolean'] + read_df.columns.tolist())

                # Ensure session_id is appended to the list of ground truth session ids if the boolean is true
                merged['paramount__ground_truth'] = merged.apply(
                    lambda row: row['paramount__ground_truth'] + [session_id] if row[
                        'paramount__ground_truth_boolean'] else row['paramount__ground_truth'],
                    axis=1
                )
                merged = merged.drop(columns=['paramount__ground_truth_boolean'])

                db_instance.update_ground_truth(merged, ground_truth_table_name)
                session_table_name = 'paramount_ground_truth_sessions'
                db_instance.create_or_append(pd.DataFrame([session_df]), session_table_name, 'session_id')

                st.session_state['full_df'] = full_df
                st.session_state['random_suggested_name'] = random_suggested_name()
                st.rerun()

            # TODO: For train mode, allow date/session/botid filters (imagine massive data).
            # TODO: For train, try with other functions such that record.py is more robust.

    else:
        st.write("No data found. Ensure you use @paramount.record decorator on any functions you want to record.")


if __name__ == '__main__':
    run()
