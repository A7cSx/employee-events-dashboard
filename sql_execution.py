import sqlite3
import pandas as pd
from pathlib import Path

# Path to the SQLite database, relative to this file
DB_PATH = Path(__file__).parent / "employee_events.db"


class QueryMixin:
    """
    Mixin class that provides reusable methods for opening a connection
    to the employee_events SQLite database, executing SQL queries,
    closing the connection, and returning the resulting data.

    Include this mixin in any class that needs database access by adding
    it to the class's inheritance chain, e.g.:
        class MyClass(QueryMixin): ...
    """

    def query_return_df(self, sql: str) -> pd.DataFrame:
        """
        Execute a SQL query and return the result as a pandas DataFrame.

        Steps performed:
        1. Opens a connection to employee_events.db
        2. Executes the provided SQL query
        3. Closes the connection
        4. Returns the data as a DataFrame
        """
        conn = sqlite3.connect(DB_PATH)
        try:
            df = pd.read_sql(sql, conn)
        finally:
            conn.close()
        return df

    def query_return_list_of_tuples(self, sql: str) -> list:
        """
        Execute a SQL query and return the result as a list of tuples.

        Steps performed:
        1. Opens a connection to employee_events.db
        2. Executes the provided SQL query
        3. Closes the connection
        4. Returns the data as a list of tuples
        """
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            result = cursor.execute(sql).fetchall()
        finally:
            conn.close()
        return result
