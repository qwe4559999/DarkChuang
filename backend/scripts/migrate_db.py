import sqlite3
import os

DB_PATH = "chemistry_bot.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(messages)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "data" not in columns:
            print("Adding 'data' column to 'messages' table...")
            cursor.execute("ALTER TABLE messages ADD COLUMN data TEXT")
            conn.commit()
            print("Migration successful.")
        else:
            print("'data' column already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
