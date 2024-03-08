import os
import pandas as pd
import numpy as np
from .db import Database
import traceback
from sqlalchemy import create_engine, inspect, Table, MetaData, select, text, desc, and_
from sqlalchemy.dialects.postgresql import JSONB, UUID, TEXT, insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from dotenv import load_dotenv, find_dotenv
import uuid
if find_dotenv():
    load_dotenv()


class PostgresDatabase(Database):
    def __init__(self):  # connection string may need postgresql+psycopg2 as prefix to work
        self.engine = create_engine(os.getenv('PARAMOUNT_POSTGRES_CONNECTION_STRING'))
        self.existing_tables = {}

    def create_or_append(self, dataframe, table_name, primary_key):
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

        cols = [primary_key] + df_copy.columns.drop(primary_key, errors='ignore').tolist()
        df_copy = df_copy[cols]
        df_copy.set_index(primary_key, inplace=True)
        dtype[primary_key] = UUID

        try:  # Try to append the copy of the DataFrame to the SQL table, handle potential SQL errors
            newly_created = not self.table_exists(table_name)
            df_copy.to_sql(table_name, self.engine, if_exists='append', dtype=dtype, index=True)

            if newly_created:
                print(f"detected newly created table, creating primary key {primary_key}")
                with self.engine.begin() as conn:
                    sql = text(f'ALTER TABLE {table_name} ADD PRIMARY KEY ({primary_key})')
                    conn.execute(sql)
        except SQLAlchemyError as e:
            if issubclass(psycopg2.errors.lookup(e.orig.pgcode), psycopg2.errors.UndefinedColumn):
                self.create_columns(df_copy, table_name)
            else:
                err_tcb = traceback.format_exc()
                print(f"An error occurred while appending to {table_name}: {e}: {err_tcb}")
                raise  # Re-raise the exception for further handling if necessary

    def create_columns(self, df, table_name):
        print(f"PARAMOUNT: UndefinedColumn error - Adding new columns to table to prevent this for future invocations")
        new_cols = [col for col in df.columns if col not in self.existing_tables.get(table_name, [])]
        for column in new_cols:
            sql = text(f'ALTER TABLE {table_name} ADD COLUMN {column} TEXT')
            with self.engine.begin() as conn:
                conn.execute(sql)
                print(f"Added column {column} to {table_name}.")
        self.existing_tables[table_name] = self.existing_tables.get(table_name, []) + new_cols

    def table_exists(self, table_name):
        if table_name in self.existing_tables:
            return self.existing_tables[table_name]
        else:
            # We can use the SQLAlchemy Inspector to check for the table
            inspector = inspect(self.engine)
            has_table = inspector.has_table(table_name)
            if has_table:
                self.existing_tables[table_name] = [col['name'] for col in inspector.get_columns(table_name)]
            return has_table

    # Not doing a full table replacement as in CSV DB, since this runs in prod and replacing tables there is a big no-no
    def update_ground_truth(self, df, table_name):
        # Replacing pd.NaT with None so DB accepts it, otherwise get: invalid input syntax for type timestamp: "NaT"
        df = df.replace({np.nan: None})

        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=self.engine)

        rows = df.to_dict(orient='records')
        unique_constraint_column = 'paramount__recording_id'  # Must pre-exist as primary key for this to work?

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

    def get_table(self, table_name, all_rows, identifier_column_name, identifier_value):
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=self.engine)

        identifier_column = table.c[identifier_column_name]  # Get the column to filter on

        # Prepare the select statement with a where clause
        stmt = (
            select(table)
            .where(
                and_(
                    identifier_column == identifier_value,  # SQLAlchemy overloads == operator to run it
                    True if all_rows else table.c.paramount__evaluation.notilike('')  # notilike: gets only eval'd rows
                )
            )
            .order_by(desc('paramount__recorded_at'))
            .limit(100)
        )
        with self.engine.connect() as conn:
            df = pd.read_sql(stmt, conn)
            df['paramount__evaluation'] = df['paramount__evaluation'].replace("", None)

            # Convert UUID cols to str so Evaluate.py merged df has a successful right join on 'paramount__record_id'
            uuid_cols = [
                col for col in df.columns
                if df[col].dtype == 'object'
                and not df[col].dropna().empty  # Ensure non-empty
                and isinstance(df[col].dropna().iloc[0], uuid.UUID)  # Check for UUID type
            ]
            df[uuid_cols] = df[uuid_cols].astype(str)

            return df
