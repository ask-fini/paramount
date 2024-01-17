from abc import ABC, abstractmethod
import os

from dotenv import load_dotenv, find_dotenv
if find_dotenv():
    load_dotenv()

env_db_key = 'PARAMOUNT_DB_TYPE'
database_type = 'csv' if env_db_key not in os.environ else os.getenv(env_db_key)


# Abstraction for Database with a generic method
class Database(ABC):
    @abstractmethod
    def create_or_append(self, dataframe, table_name):
        pass

    @abstractmethod
    def table_exists(self, table_name):
        pass

    @abstractmethod
    def get_records(self, table_name):
        pass

    @abstractmethod
    def update_ground_truth(self, df, table_name):
        pass

    @abstractmethod
    def get_sessions(self, table_name):
        pass


# Factory method to instantiate the concrete class
def get_database():
    # Must do lazy imports here inside the function to avoid circular dependency errors
    from .csv import CSVDatabase
    from .postgres import PostgresDatabase
    dbdict = {'csv': CSVDatabase, 'postgres': PostgresDatabase}
    if database_type in dbdict:
        print(f"Using database type: {database_type}, for paramount ground truth recordings")
        return dbdict[database_type]()
    else:
        raise ValueError(f"Unsupported db: {database_type} (env var {env_db_key} should be one of {dbdict.keys()})")
