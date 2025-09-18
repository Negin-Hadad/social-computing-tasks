# pip install pandas
import sqlite3
import pandas as pd

DB_FILE = r"e:\OuluUni\period1\SocialComputing\assignments\database.sqlite"

try:
    conn = sqlite3.connect(DB_FILE)
    print("SQLite DB connection successful")
except Exception as e:
    print(f"Error in connecting to DB: '{e}'")

# Task 1.1
tableNames_df = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
print(f'table names:\n {tableNames_df}')

for table in ['users', 'posts', 'comments', 'reactions', 'follows']:
    tableContent = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    print(f'\nTable "{table}" number of rows: {len(tableContent)}')
    print(f'\nTable "{table}" columns description:')
    columns = pd.read_sql_query(f"PRAGMA table_info({table})", conn)
    print(columns[["name", "type"]])
    print("-------------------------------")
    

conn.close()