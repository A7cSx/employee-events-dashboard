import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / 'employee_events.db'

class QueryMixin:
    def query_return_df(self, sql):
        conn = sqlite3.connect(DB_PATH)
        try:
            df = pd.read_sql(sql, conn)
        finally:
            conn.close()
        return df

    def query_return_list_of_tuples(self, sql):
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            result = cursor.execute(sql).fetchall()
        finally:
            conn.close()
        return result
