import sqlite3
import os

DB_PATH = "chemistry_bot.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found. It will be created by the app.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Check if users table exists (it might be created by app startup, but good to check)
        # Actually, let's rely on app startup for table creation, or create it here if we want to be safe.
        # But adding columns to existing tables is the main job here.

        # 2. Add user_id to conversations
        cursor.execute("PRAGMA table_info(conversations)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "user_id" not in columns:
            print("Adding 'user_id' column to 'conversations' table...")
            cursor.execute("ALTER TABLE conversations ADD COLUMN user_id INTEGER REFERENCES users(id)")
            conn.commit()
            print("Migration successful: Added user_id to conversations.")
        else:
            print("'user_id' column already exists in conversations.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
