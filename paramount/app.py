import pandas as pd
import streamlit as st
from glob import glob
import uuid
st.set_page_config(layout="wide")

colors = {
    'paramount_': '#ACCBE1',  # Soft blue
    'input_': '#C2E0C6',  # Pale green
    'output_': '#FFF2CC',  # Light yellow
}


def color_columns(df: pd.DataFrame):
    # Create a color map based on column prefixes
    color_map = {col: f'background-color: {color}' for prefix, color in colors.items() for col in df.columns if col.startswith(prefix)}

    # Styling function to apply color_map
    styler = df.style.apply(lambda x: [color_map.get(x.name, '') for _ in x], axis=0)

    # Return the styler to display the DataFrame with the colored columns
    return styler


def run():
    st.title('Paramount')
    files = sorted(glob('paramount_data_*.csv'))

    df_list = []

    possible_cols = []

    if len(files) > 0:
        for idx, file in enumerate(files):
            temp_df = pd.read_csv(file)
            df_list.append(temp_df)
            possible_cols += [col for col in temp_df.columns if col not in possible_cols]

        input_cols = [col for col in possible_cols if col.startswith("input_")]
        output_cols = [col for col in possible_cols if col.startswith("output_")]

        paramount_suffix = ['recording_id', 'timestamp', 'function_name', 'execution_time']
        paramount_cols = ['paramount_' + suffix for suffix in paramount_suffix]
        identifier_cols = paramount_cols + input_cols

        format_func = lambda col: "_".join(col.split("_")[1:]) if "_" in col else col

        col_mapping = {'paramount_': paramount_cols, 'input_': input_cols, 'output_': output_cols}

        # Generate CSS selectors and rules
        css_rules = []
        for prefix, cols in col_mapping.items():
            color = colors.get(prefix)
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
            filtered_cols = ['paramount_ground_truth', 'paramount_recording_id'] + selected_id_cols + selected_input_cols + selected_output_cols
            filtered_cols = list(dict.fromkeys(filtered_cols))  # Avoids column name duplication but maintains order
            selection_made = True

        # Now decide what DataFrame to use for the data_editor based on session state
        if 'edited_df' in st.session_state:
            df_merged = st.session_state['edited_df'][filtered_cols]
        else:
            df_merged = pd.concat(df_list)[filtered_cols].reset_index(drop=True)
            # Turn session_id into a checkbox in the UI
            df_merged['paramount_ground_truth'] = df_merged['paramount_ground_truth'].apply(
                lambda x: False if pd.isna(x) else bool(str(x).strip()))

        # Turn it into a checkbox

        disabled_cols = set([col for col in df_merged.columns if col != "paramount_ground_truth"])

        column_config = {col: format_func(col) for col in df_merged.columns}

        # paramount_recording_id needs to always be present in DF, for the pd.merge in session saving to work
        if selection_made and "paramount_recording_id" not in selected_id_cols:
            column_config['paramount_recording_id'] = None  # Hides the column

        def on_change(edited_df):  # Needed to ensure UI updates are synchronized correctly across ground truth clicks
            st.session_state['edited_df'] = edited_df

        edited_df = st.data_editor(data=color_columns(df_merged), column_config=column_config,
                                   use_container_width=True, disabled=disabled_cols, hide_index=True,
                                   on_change=on_change, args=(df_merged,))

        _, save_col, _ = st.columns(3)

        # TODO: Save the session data itself into a session.csv file
        with save_col:
            if st.button("Save session"):
                session_id = str(uuid.uuid4())
                for original_df, file in zip(df_list, files):
                    merged = pd.merge(edited_df[['paramount_ground_truth', 'paramount_recording_id']],
                                      original_df.drop(columns='paramount_ground_truth', errors='ignore'),
                                      on='paramount_recording_id', how='right')

                    merged['paramount_ground_truth'] = merged['paramount_ground_truth'].apply(
                        lambda x: session_id if x else '')
                    merged.to_csv(file, index=False)
                st.session_state['edited_df'] = edited_df

        # TODO: In train mode, allow date filters (imagine massive data).
        # Then once user is happy with ground truth, save edited_df with button. updates original recording file
        # Challenge: How do the filters interplay with what's saved? Saved_df needs all params for replay
        # Maybe a "saved_session" of ground truths is its own entry in a separate table, including filter settings
        # Probably each row of ground truths need to be associated to a session ID in that case
        # TODO: In test mode, load in the ground truth table belonging to a session ID
        # User selects "param to vary", and specifies a new value to test with. then clicks "Test" button
        # Also accuracy measurement function choice will have to be made eg cosine distance
        # Challenge: How to replay in the UI - How to invoke the recorded function? Will need env vars from prod enviro?
        # Best way to do it is probably co-run (on diff port) with whichever production docker the user is using
        # Eg as an addition of "paramount *" on top of whichever pre-existing Docker run command (CMD exec)

    else:
        st.write("No data files found. Ensure you use @paramount.record decorator on any functions you want to record.")


if __name__ == '__main__':
    run()
