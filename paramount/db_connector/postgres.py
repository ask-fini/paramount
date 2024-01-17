import os
from .db import Database
from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv
if find_dotenv():
    load_dotenv()


class PostgresDatabase(Database):
    def __init__(self):  # connection string may need postgresql+psycopg2 as prefix to work
        self.engine = create_engine(os.getenv('PARAMOUNT_POSTGRES_CONNECTION_STRING'))

    def create_or_append(self, dataframe, table_name):
        # Note that this will create a new table or append if it exists, and does not handle schema migrations.
        dataframe.to_sql(table_name, self.engine, if_exists='append', index=False)

    def table_exists(self, table_name):
        pass

    def update_ground_truth(self, df, table_name):
        pass

    def get_records(self, table_name):
        pass

    def get_sessions(self, table_name):
        pass
