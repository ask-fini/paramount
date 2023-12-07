import pandas as pd
import streamlit as st
from glob import glob


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
    else:
        st.write("No data files found. Ensure you use @paramount.record decorator on any functions you want to record.")

    input_cols = [col for col in possible_cols if not col.startswith("output_") or not col.split("_")[1].isdigit()]
    output_cols = [col for col in possible_cols if col.startswith("output_") and col.split("_")[1].isdigit()]
    identifier_cols = input_cols

    selected_id_cols = st.multiselect('Identifiers', identifier_cols)
    selected_input_cols = st.multiselect('Input columns', input_cols)
    selected_output_cols = st.multiselect('Output columns', output_cols)

    if not selected_id_cols and not selected_input_cols and not selected_output_cols:
        filtered_cols = possible_cols
    else:
        filtered_cols = selected_id_cols + selected_input_cols + selected_output_cols

    df_list = [df[filtered_cols] for df in df_list]

    for idx, df in enumerate(df_list):
        st.data_editor(data=df, key=f"df_editor_{idx}", use_container_width=True)
        st.write("---")


if __name__ == '__main__':
    run()
