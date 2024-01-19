import os
import pandas as pd
from .db import Database
import traceback
from sqlalchemy import create_engine, inspect, Table, MetaData, select
from sqlalchemy.dialects.postgresql import JSONB, UUID, TEXT, insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv, find_dotenv
import uuid
if find_dotenv():
    load_dotenv()


class PostgresDatabase(Database):
    def __init__(self):  # connection string may need postgresql+psycopg2 as prefix to work
        self.engine = create_engine(os.getenv('PARAMOUNT_POSTGRES_CONNECTION_STRING'))
        self.existing_tables = {}

    def create_or_append(self, dataframe, table_name):
        # Make a copy of the DataFrame to avoid modifying the original
        df_copy = dataframe.copy()
        dtype = {}

        for col in df_copy.columns:
            # Get the first non-null element in the column
            first_non_null = df_copy[col].dropna().iloc[0] if not df_copy[col].dropna().empty else None
            if first_non_null is not None:
                # If the first non-null element is a string, use the string data type
                if isinstance(first_non_null, str):
                    dtype[col] = TEXT
                # If the first non-null element is a list or dict, use JSONB data type
                elif isinstance(first_non_null, (list, dict)):
                    dtype[col] = JSONB

        cols = ['paramount__recording_id'] + df_copy.columns.drop('paramount__recording_id', errors='ignore').tolist()
        df_copy = df_copy[cols]
        df_copy.set_index('paramount__recording_id', inplace=True)
        dtype['paramount__recording_id'] = UUID

        try:  # Try to append the copy of the DataFrame to the SQL table, handle potential SQL errors
            df_copy.to_sql(table_name, self.engine, if_exists='append', dtype=dtype, index=True)
            print(f"Data appended to {table_name} successfully.")
        except SQLAlchemyError as e:
            err_tcb = traceback.format_exc()
            print(f"An error occurred while appending to {table_name}: {e}: {err_tcb}")
            raise  # Re-raise the exception for further handling if necessary

    def table_exists(self, table_name):
        if table_name in self.existing_tables:
            return True
        else:
            # We can use the SQLAlchemy Inspector to check for the table
            inspector = inspect(self.engine)
            has_table = inspector.has_table(table_name)
            if has_table:
                self.existing_tables[table_name] = True
            return has_table

    # Not doing a full table replacement as in CSV DB, since this runs in prod and replacing tables there is a big no-no
    def update_ground_truth(self, df, table_name):
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=self.engine)

        rows = df.to_dict(orient='records')
        unique_constraint_column = 'paramount__recording_id'

        upsert_stmt = pg_insert(table).on_conflict_do_update(  # Bulk update, overwrites old cells on conflict
            index_elements=[unique_constraint_column],
            set_={
                c.name: pg_insert(table).excluded[c.name]
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
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=self.engine)
        stmt = select(table)
        with self.engine.connect() as conn:
            df = pd.read_sql(stmt, conn)
            df['paramount__ground_truth'] = df['paramount__ground_truth'].replace("", None)

            # Convert UUID cols to str so Train.py merged df has a successful right join on 'paramount__record_id'
            uuid_cols = [
                col for col in df.columns
                if df[col].dtype == 'object'
                and not df[col].dropna().empty  # Ensure non-empty
                and isinstance(df[col].dropna().iloc[0], uuid.UUID)  # Check for UUID type
            ]
            df[uuid_cols] = df[uuid_cols].astype(str)

            for col in df.columns:
                if df[col].apply(lambda x: isinstance(x, list)).any():
                    # If any element within the column is a list, convert the whole column
                    df[col] = df[col].astype(str)
            return df
