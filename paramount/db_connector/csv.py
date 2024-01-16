# CSV implementation
from db import Database
import os


class CSVDatabase(Database):
    def __init__(self, filepath):
        self.filepath = filepath

    def create_or_append(self, dataframe, table_name):
        if_exists_option = 'append' if os.path.isfile(self.filepath) else 'replace'
        dataframe.to_csv(self.filepath, mode='a', header=not os.path.exists(self.filepath), index=False, if_exists=if_exists_option)