import pandas as pd
import streamlit as st
from glob import glob


def color_columns(df: pd.DataFrame):
    # Define the color for each prefix
    colors = {
        'paramount_': 'background-color: #ACCBE1',  # Soft blue
        'input_': 'background-color: #C2E0C6',  # Pale green
        'output_': 'background-color: #FFF2CC',  # Light yellow
    }

    # Create a color map based on column prefixes
    color_map = {col: color for prefix, color in colors.items() for col in df.columns if col.startswith(prefix)}

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
        identifier_cols = input_cols

        format_func = lambda col: "_".join(col.split("_")[1:]) if "_" in col else col

        paramount_cols = ['paramount_ground_truth', 'paramount_timestamp']

        # Styling
        input_selectors = [f'[aria-label^="{col.replace("input_", "")}"]' for col in input_cols]
        output_selectors = [f'[aria-label^="{col.replace("output_", "")}"]' for col in output_cols]
        input_css_selectors = ", ".join(input_selectors)
        output_css_selectors = ", ".join(output_selectors)
        st.markdown(f"""
        <style>
        /* Style for input tags */
        {input_css_selectors} {{
            background-color: #C2E0C6; /* Pale green */
            color: black;
        }}

        /* Style for output tags */
        {output_css_selectors} {{
            background-color: #FFF2CC; /* Light yellow */
            color: black;
        }}
        </style>
        """, unsafe_allow_html=True)

        selected_id_cols = st.multiselect('Identifiers', identifier_cols, format_func=format_func)
        selected_input_cols = st.multiselect('Input columns', input_cols, format_func=format_func)
        selected_output_cols = st.multiselect('Output columns', output_cols, format_func=format_func)

        if not selected_id_cols and not selected_input_cols and not selected_output_cols:
            filtered_cols = possible_cols
        else:
            filtered_cols = paramount_cols + selected_id_cols + selected_input_cols + selected_output_cols

        df_merged = pd.concat([df[filtered_cols] for df in df_list])
        df_merged = df_merged.reset_index(drop=True)
        disabled_cols = set([col for col in df_merged.columns if col != "paramount_ground_truth"])

        column_config = {col: format_func(col) for col in df_merged.columns}

        st.data_editor(data=color_columns(df_merged), column_config=column_config,
                       use_container_width=True, disabled=disabled_cols)
    else:
        st.write("No data files found. Ensure you use @paramount.record decorator on any functions you want to record.")


if __name__ == '__main__':
    run()
