from abc import ABC, abstractmethod
from .csv import CSVDatabase
from .postgres import PostgresDatabase


# Abstraction for Database with a generic method
class Database(ABC):
    @abstractmethod
    def create_or_append(self, dataframe, table_name):
        pass


# Factory method to instantiate the concrete class
def get_database(database_type, **kwargs):
    if database_type == 'csv':
        return CSVDatabase(kwargs['filepath'])
    elif database_type == 'postgres':
        return PostgresDatabase(kwargs['username'], kwargs['password'], kwargs['host'], kwargs['port'], kwargs['db_name'])
    else:
        raise ValueError("Unsupported database type")
