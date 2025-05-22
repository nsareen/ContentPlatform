"""
Script to apply database migrations directly using SQLAlchemy
"""
import os
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Text, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.sql import text
from datetime import datetime
import enum

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the database models and enums
from app.models.models import BrandVoiceStatus

# Database URL - using SQLite for development
DATABASE_URL = "sqlite:///./sql_app.db"

def run_migration():
    """Apply the migration to add the brand_voice_versions table"""
    print("Starting migration...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Check if the table already exists
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    if 'brand_voice_versions' in metadata.tables:
        print("Table 'brand_voice_versions' already exists.")
        
        # Check if published_at column exists
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(brand_voice_versions)"))
            columns = [row[1] for row in result]
            
            if 'published_at' not in columns:
                print("Adding 'published_at' column to 'brand_voice_versions' table...")
                conn.execute(text("ALTER TABLE brand_voice_versions ADD COLUMN published_at TIMESTAMP"))
                print("Column 'published_at' added successfully.")
            else:
                print("Column 'published_at' already exists.")
    else:
        print("Creating 'brand_voice_versions' table...")
        
        # Create the table
        with engine.connect() as conn:
            conn.execute(text("""
            CREATE TABLE brand_voice_versions (
                id VARCHAR PRIMARY KEY,
                brand_voice_id VARCHAR NOT NULL,
                version_number INTEGER NOT NULL,
                name VARCHAR NOT NULL,
                description TEXT,
                voice_metadata JSON,
                dos TEXT,
                donts TEXT,
                status VARCHAR NOT NULL,
                created_by_id VARCHAR,
                created_at TIMESTAMP NOT NULL,
                published_at TIMESTAMP,
                FOREIGN KEY (brand_voice_id) REFERENCES brand_voices (id),
                FOREIGN KEY (created_by_id) REFERENCES users (id)
            )
            """))
            
            print("Table 'brand_voice_versions' created successfully.")
    
    print("Migration completed successfully.")

if __name__ == "__main__":
    run_migration()
