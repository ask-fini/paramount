import pandas as pd
import streamlit as st
import os
import uuid
import pytz
from datetime import datetime
from paramount.library_functions import (
    hide_buttons,
    random_suggested_name,
    color_columns,
    get_colors,
    format_func,
    large_centered_button,
)
st.set_page_config(layout="wide")


def run():
    hide_buttons()
    st.title('Record ground truth data')

    filename = 'paramount_data.csv'
    if os.path.isfile(filename):
        read_df = pd.read_csv(filename)
        possible_cols = read_df.columns

        input_cols = [col for col in possible_cols if col.startswith("input_")]
        output_cols = [col for col in possible_cols if col.startswith("output_")]

        paramount_suffix = ['recording_id', 'timestamp', 'function_name', 'execution_time']
        paramount_cols = ['paramount_' + suffix for suffix in paramount_suffix]
        identifier_cols = paramount_cols + input_cols

        col_mapping = {'paramount_': paramount_cols, 'input_': input_cols, 'output_': output_cols}

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
            filtered_cols = ['paramount_ground_truth'] + selected_id_cols + selected_input_cols + selected_output_cols
            filtered_cols = list(dict.fromkeys(filtered_cols))  # Avoids column name duplication but maintains order
            selection_made = True

        # Now decide what DataFrame to use for the data_editor based on session state
        if 'full_df' in st.session_state:
            full_df = st.session_state['full_df']
        else:
            full_df = read_df.reset_index(drop=True)
            # Turn session_id into a checkbox in the UI
            full_df['paramount_ground_truth'] = full_df['paramount_ground_truth'].apply(
                lambda x: False if pd.isna(x) else bool(str(x).strip()))

        disabled_cols = set([col for col in full_df.columns if col not in ["paramount_ground_truth"] + selected_output_cols])

        column_config = {col: format_func(col) for col in full_df.columns}

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
        if selection_made:
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
                    'session_all_possible_cols': list(possible_cols)
                }

                # Including selected_output_cols in the merge, in order to include any UI edits done for the outputs
                merged = pd.merge(full_df[['paramount_ground_truth', 'paramount_recording_id']+selected_output_cols],
                                  read_df.drop(columns=['paramount_ground_truth']+selected_output_cols,
                                               errors='ignore'), on='paramount_recording_id', how='right')

                merged = merged.reindex(columns=read_df.columns)  # To not mess up the order of output cols

                merged['paramount_ground_truth'] = merged['paramount_ground_truth'].apply(
                    lambda x: session_id if x else '')
                merged.to_csv(filename, index=False)

                session_csv = 'paramount_ground_truth_sessions.csv'
                pd.DataFrame([session_df]).to_csv(session_csv, mode='a',
                                                  header=not pd.io.common.file_exists(session_csv), index=False)
                st.session_state['full_df'] = full_df
                st.session_state['random_suggested_name'] = random_suggested_name()
                st.rerun()

            # TODO: For train mode, allow date/session/botid filters (imagine massive data).
            # TODO: For train, try with other functions such that record.py is more robust.

    else:
        st.write("No data found. Ensure you use @paramount.record decorator on any functions you want to record.")


if __name__ == '__main__':
    run()
