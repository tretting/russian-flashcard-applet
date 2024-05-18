import sqlite3
import pandas as pd

# The name of the SQLite database file
db_filename = 'russian_flashcards.db'

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(db_filename)

# Load each CSV file into a DataFrame, sort it, and then insert it into the SQLite database
def load_csv_to_db(csv_file, table_name, conn):
    df = pd.read_csv(csv_file)

    # Special sorting for the 'words_forms' table
    if table_name == 'words_forms':
        if 'id' in df.columns and 'word_id' in df.columns:
            df = df.sort_values(by=['id', 'word_id'])
            
    # General sorting by 'word_id' for other tables
    elif 'word_id' in df.columns:
        df = df.sort_values(by='word_id')

    df.to_sql(table_name, conn, if_exists='replace', index=False)

# List of CSV files and corresponding table names
csv_files_and_tables = [
    ('ru_nou.csv', 'nouns'),
    ('ru_adj.csv', 'adjectives'),
    ('ru_words.csv', 'words'),
    ('ru_words_forms.csv', 'words_forms'),
    ('ru_ver.csv', 'verbs'),
    ('ru_sen.csv', 'sentences'),
    ('ru_tra.csv', 'translations'),
    # Add more if you have other tables
]

# Process each CSV file
for csv_file, table_name in csv_files_and_tables:
    load_csv_to_db(csv_file, table_name, conn)

# Commit changes and close the connection
conn.commit()
conn.close()

print("CSV files have been successfully loaded into the SQLite database.")
