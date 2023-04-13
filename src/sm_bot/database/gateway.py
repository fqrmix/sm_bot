import psycopg2
from psycopg2.extras import execute_values
from typing import (List, Tuple, Union, Dict)
from .config import DatabaseConfig
from .exceptions import DbConnectionNotOpened
from .models import DatabaseObject

class DatabaseGateway:
    """
    Gateway class to interact with PostgreSQL database

    Public methods
    -------
    open_connection()
        Opening connection to PostgreSQL database

    close_connection()
        Closing connection to PostgreSQL database

    fetch_all(table: str, columns: List[str])
        Fetching specific columns from specific table

        SQL query: SELECT columns FROM table;
    
    fetch_by_value(table: str, columns: List[str], param: str, value: str)
        Fetching specific columns from specific table, where param equals value

        SQL query: SELECT columns FROM table WHERE param=value;

    insert(table: str, column_values: dict)
        Inserting selected rows to specific table.

        rows names and values explained as a dictionary with following format:
        {
            'row1_name': 'row1_value',
            'row2_name': 'row2_value',
            ...
            'rowN_name': 'rowN_value'
        }

        SQL query: INSERT INTO table (row1_name, row2_name, ...) row1_value, row2_value, ...;

    execute_query(query: str, columns: List[str] *optional)
        Executing specific query

        SQL query: {query}
    """
    def __init__(self) -> None:
        self._connection = None
    
    def fetch_all(self, table: str) -> Union[DatabaseObject, None]:
        try:
            return self._raw_sql_execute(f"SELECT * FROM {table}")
        except Exception as error:
            print(error)

    def fetch_by_value(self, 
                       table: str, 
                       param: str, 
                       value: str) -> Union[DatabaseObject, None]:
        try: 
            return self._raw_sql_execute(
                f"SELECT * FROM {table} WHERE {param}='{value}'"
            )
        except Exception as error:
            print(error)
    
    def insert(self, table: str, column_values: dict) -> None:
        columns = ', '.join(column_values.keys())
        values = [tuple(column_values.values())]
        print(values)
        try:
            self._raw_execute_values(
                f"INSERT into {table} "
                f"({columns}) "
                f"VALUES %s;",
                values
            )
        except Exception as error:
            print(error)

    def execute_query(self, query: str) -> Union[DatabaseObject, None]:
        try:
            return self._raw_sql_execute(query=query)
        except Exception as error:
            print(error)

    def _raw_sql_execute(self, query: str) -> DatabaseObject:
        if self._connection:
            with self._connection.cursor() as _cursor:
                _cursor.execute(query)
                columns = [desc[0] for desc in _cursor.description]
                return DatabaseObject(rows=_cursor.fetchall(), columns=columns)
        else:
            raise DbConnectionNotOpened('Connection to PostgreSQL has not been opened!')

    def _raw_execute_values(self, query: str, values: List[Tuple]) -> None:
        if self._connection:
            with self._connection.cursor() as _cursor:
                execute_values(
                    cur=_cursor,
                    sql=query,
                    argslist=values
                )
            self._connection.commit()
        else:
            raise DbConnectionNotOpened('Connection to PostgreSQL has not been opened!')

    def open_connection(self) -> None:
        # Establish connection to PostgreSQL
        if not self._connection:
            self._connection = psycopg2.connect(
                user=DatabaseConfig.USER,
                password=DatabaseConfig.PASSWORD,
                database=DatabaseConfig.DATABASE_NAME
            )
            print("[INFO] Connection to PostgreSQL has been established")
        else:
            print("[INFO] Connection to PostgreSQL was already established")

    def close_connection(self) -> None:
        # Close connection to PostgreSQL
        if self._connection:
            self._connection.close()
            print("[INFO] Connection to PostgreSQL has been closed")
        else:
            print("[INFO] Connection to PostgreSQL was already closed")
