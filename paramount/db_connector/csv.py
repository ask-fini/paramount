# CSV implementation
from .db import Database
import os
import pandas as pd


class CSVDatabase(Database):
    def create_or_append(self, df, table_name, primary_key=None):
        # Check if the file exists, and if not, create it with header, else append without header
        filename = table_name+'.csv'
        if not os.path.isfile(filename):
            df.to_csv(filename, mode='a', index=False)
        else:
            df.to_csv(filename, mode='a', index=False, header=False)

    def table_exists(self, table_name):
        return os.path.isfile(table_name+'.csv')

    def update_ground_truth(self, df, table_name):
        df.to_csv(table_name+'.csv', index=False)

    def get_table(self, table_name, records_data=None, identifier_column_name=None, identifier_value=None):
        return pd.read_csv(table_name+'.csv')
