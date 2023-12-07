import pandas as pd
import streamlit as st
from glob import glob


def run():
    st.title('Paramount')

    # Loop through all files that match the pattern 'paramount_data_*.csv'
    files = sorted(glob('paramount_data_*.csv'))
    if len(files) > 0:
        for file in files:
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file)
            # Use st.data_editor to display the DataFrame
            st.data_editor(data=df, use_container_width=True)
            # Add some space after each table for readability
            st.write("---")
    else:
        st.write("No data files found. Ensure you use @paramount.record decorator on any functions you want to record.")


if __name__ == '__main__':
    run()
