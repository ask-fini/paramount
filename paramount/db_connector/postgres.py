import os
from db import Database
from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv
if find_dotenv():
    load_dotenv()

base_url = os.getenv('FUNCTION_API_BASE_URL')


# PostgreSQL implementation
class PostgresDatabase(Database):
    def __init__(self, username, password, host, port, db_name):
        self.engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}')

    def create_or_append(self, dataframe, table_name):
        # Note that this will create a new table or append if it exists, and does not handle schema migrations.
        dataframe.to_sql(table_name, self.engine, if_exists='append', index=False)