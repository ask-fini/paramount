import os
import pandas as pd
from .db import Database
import traceback
from sqlalchemy import create_engine, inspect, Table, MetaData
from sqlalchemy.dialects.postgresql import insert
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
        # We can use the SQLAlchemy Inspector to check for the table
        inspector = inspect(self.engine)
        has_table = inspector.has_table(table_name)
        return has_table

    # Not doing a full table replacement as in CSV DB, since this runs in prod and replacing tables there is a big no-no
    def update_ground_truth(self, df, table_name):
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=self.engine)

        rows = df.to_dict(orient='records')
        unique_constraint_column = 'paramount__recording_id'

        upsert_stmt = insert(table).on_conflict_do_update(  # Bulk update, overwrites old cells on conflict
            index_elements=[unique_constraint_column],
            set_={
                c.name: insert(table).excluded[c.name]
                for c in table.c
                if c.name != unique_constraint_column
            }
        )

        try:
            with self.engine.begin() as connection:
                connection.execute(upsert_stmt, rows)
        except Exception as e:
            err_tcb = traceback.format_exc()
            print(f"{e}: {err_tcb}")
            raise

    def get_table(self, table_name):
        with self.engine.connect() as connection:
            query = f"SELECT * FROM {table_name};"
            return pd.read_sql_query(sql=query, con=connection)
