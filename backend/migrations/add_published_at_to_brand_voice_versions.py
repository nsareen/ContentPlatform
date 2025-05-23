"""
Migration script to add published_at column to brand_voice_versions table.
"""
import sqlite3
import os
from datetime import datetime

def run_migration():
    """Add published_at column to brand_voice_versions table."""
    # Get the database path from environment variable or use default
    db_path = os.environ.get('DATABASE_URL', 'sqlite:///./content_platform.db')
    
    # Extract the actual path for SQLite
    if db_path.startswith('sqlite:///'):
        db_path = db_path[len('sqlite:///'):]
    
    print(f"Running migration on database: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(brand_voice_versions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'published_at' not in columns:
            print("Adding published_at column to brand_voice_versions table...")
            
            # Add the published_at column
            cursor.execute("""
                ALTER TABLE brand_voice_versions
                ADD COLUMN published_at TIMESTAMP
            """)
            
            print("Column added successfully.")
        else:
            print("published_at column already exists in brand_voice_versions table.")
        
        # Commit the changes
        conn.commit()
        print("Migration completed successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
