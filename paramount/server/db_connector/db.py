from abc import ABC, abstractmethod


# Abstraction for Database with a generic method
class Database(ABC):
    @abstractmethod
    def create_or_append(self, dataframe, table_name, primary_key):
        pass

    @abstractmethod
    def table_exists(self, table_name):
        pass

    @abstractmethod
    def update_ground_truth(self, df, table_name):
        pass

    @abstractmethod
    def get_table(self, table_name, evaluated_rows_only, split_by_id, identifier_column_name, identifier_value):
        pass


# Factory method to instantiate the concrete class
def get_database(database_type, connection_string=None):
    # Must do lazy imports here inside the function to avoid circular dependency errors
    from .csv import CSVDatabase
    from .postgres import PostgresDatabase
    dbdict = {'csv': CSVDatabase, 'postgres': PostgresDatabase}
    if database_type in dbdict:
        print(f"Using database type: {database_type}, for paramount ground truth recordings")
        if database_type == 'postgres':
            return dbdict[database_type](connection_string)
        else:
            return dbdict[database_type]()
    else:
        raise ValueError(f"Unsupported db: {database_type} (should be one of {dbdict.keys()})")
