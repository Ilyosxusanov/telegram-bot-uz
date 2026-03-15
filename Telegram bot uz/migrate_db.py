import sqlite3
import os

db_path = 'database/bot_db.sqlite'

def migrate():
    if not os.path.exists(db_path):
        print("Database not found. init_db will handle it.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add columns if they don't exist
    columns_to_add = {
        'users': [
            ('language', "TEXT DEFAULT 'uz'")
        ],
        'movies': [
            ('imdb_rating', "REAL DEFAULT 0.0"),
            ('search_count', "INTEGER DEFAULT 0")
        ]
    }
    
    for table, columns in columns_to_add.items():
        # Get existing columns
        cursor.execute(f"PRAGMA table_info({table})")
        existing_cols = [col[1] for col in cursor.fetchall()]
        
        for col_name, col_def in columns:
            if col_name not in existing_cols:
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
                    print(f"Added column {col_name} to table {table}")
                except Exception as e:
                    print(f"Error adding {col_name} to {table}: {e}")
            else:
                print(f"Column {col_name} already exists in {table}")
                
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
