#!/usr/bin/env python3
"""
Script to fix missing auto_activated columns in the database.
This script can be run manually to add the missing columns that are causing the errors.
"""

import os
import sys
from sqlalchemy import text, create_engine
from sqlalchemy.exc import ProgrammingError

def fix_missing_columns():
    """Add missing auto_activated columns to scheduled_call and session tables"""
    
    # Get database URL from environment
    database_url = os.environ.get("DATABASE_URL", "sqlite:///skileez.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print(f"Connecting to database: {database_url}")
    
    # Create engine
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        # Check database type
        is_postgresql = 'postgresql' in database_url.lower()
        is_sqlite = 'sqlite' in database_url.lower()
        
        if is_postgresql:
            print("Detected PostgreSQL database - applying column fixes...")
            fix_postgresql_columns(conn)
        elif is_sqlite:
            print("Detected SQLite database - applying column fixes...")
            fix_sqlite_columns(conn)
        else:
            print("Unknown database type - skipping column fixes")
            return

def fix_postgresql_columns(conn):
    """Fix missing columns in PostgreSQL database"""
    
    # List of columns to add to scheduled_call table
    scheduled_call_columns = [
        ("auto_activated", "BOOLEAN DEFAULT FALSE"),
        ("reminder_sent", "BOOLEAN DEFAULT FALSE"),
        ("early_join_enabled", "BOOLEAN DEFAULT TRUE"),
        ("buffer_minutes", "INTEGER DEFAULT 0"),
        ("waiting_room_enabled", "BOOLEAN DEFAULT TRUE"),
        ("calendar_event_id", "VARCHAR(255)"),
        ("calendar_provider", "VARCHAR(50)"),
        ("meeting_started_at", "TIMESTAMP"),
        ("meeting_ended_at", "TIMESTAMP"),
    ]
    
    # List of columns to add to session table
    session_columns = [
        ("auto_activated", "BOOLEAN DEFAULT FALSE"),
        ("reminder_sent", "BOOLEAN DEFAULT FALSE"),
        ("early_join_enabled", "BOOLEAN DEFAULT TRUE"),
        ("buffer_minutes", "INTEGER DEFAULT 0"),
        ("meeting_started_at", "TIMESTAMP"),
        ("meeting_ended_at", "TIMESTAMP"),
        ("waiting_room_enabled", "BOOLEAN DEFAULT TRUE"),
        ("calendar_event_id", "VARCHAR(255)"),
        ("calendar_provider", "VARCHAR(50)"),
    ]
    
    # Add columns to scheduled_call table
    print("Checking scheduled_call table...")
    for column_name, column_type in scheduled_call_columns:
        try:
            # Check if column exists
            result = conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'scheduled_call' 
                AND column_name = '{column_name}'
                AND table_schema = 'public';
            """))
            
            if not result.fetchone():
                # Column doesn't exist, add it
                conn.execute(text(f"ALTER TABLE scheduled_call ADD COLUMN {column_name} {column_type};"))
                conn.commit()
                print(f"✓ Added {column_name} column to scheduled_call table")
            else:
                print(f"✓ {column_name} column already exists in scheduled_call table")
                
        except Exception as e:
            conn.rollback()
            if "already exists" in str(e) or "duplicate column name" in str(e):
                print(f"✓ {column_name} column already exists in scheduled_call table")
            else:
                print(f"✗ Error adding {column_name} column to scheduled_call table: {e}")
    
    # Add columns to session table
    print("Checking session table...")
    for column_name, column_type in session_columns:
        try:
            # Check if column exists
            result = conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'session' 
                AND column_name = '{column_name}'
                AND table_schema = 'public';
            """))
            
            if not result.fetchone():
                # Column doesn't exist, add it
                conn.execute(text(f"ALTER TABLE session ADD COLUMN {column_name} {column_type};"))
                conn.commit()
                print(f"✓ Added {column_name} column to session table")
            else:
                print(f"✓ {column_name} column already exists in session table")
                
        except Exception as e:
            conn.rollback()
            if "already exists" in str(e) or "duplicate column name" in str(e):
                print(f"✓ {column_name} column already exists in session table")
            else:
                print(f"✗ Error adding {column_name} column to session table: {e}")
    
    print("PostgreSQL database column fixes completed!")

def fix_sqlite_columns(conn):
    """Fix missing columns in SQLite database"""
    
    # For SQLite, we need to recreate the table to add columns
    # This is a simplified approach - in production, you'd want to be more careful
    
    print("SQLite column fixes - checking if columns exist...")
    
    # Check scheduled_call table
    try:
        result = conn.execute(text("PRAGMA table_info(scheduled_call);"))
        columns = [row[1] for row in result.fetchall()]
        
        missing_columns = []
        if 'auto_activated' not in columns:
            missing_columns.append('auto_activated BOOLEAN DEFAULT 0')
        if 'reminder_sent' not in columns:
            missing_columns.append('reminder_sent BOOLEAN DEFAULT 0')
        if 'early_join_enabled' not in columns:
            missing_columns.append('early_join_enabled BOOLEAN DEFAULT 1')
        if 'buffer_minutes' not in columns:
            missing_columns.append('buffer_minutes INTEGER DEFAULT 0')
        if 'waiting_room_enabled' not in columns:
            missing_columns.append('waiting_room_enabled BOOLEAN DEFAULT 1')
        if 'calendar_event_id' not in columns:
            missing_columns.append('calendar_event_id VARCHAR(255)')
        if 'calendar_provider' not in columns:
            missing_columns.append('calendar_provider VARCHAR(50)')
        if 'meeting_started_at' not in columns:
            missing_columns.append('meeting_started_at DATETIME')
        if 'meeting_ended_at' not in columns:
            missing_columns.append('meeting_ended_at DATETIME')
        
        if missing_columns:
            print(f"Adding missing columns to scheduled_call table: {missing_columns}")
            for column_def in missing_columns:
                try:
                    conn.execute(text(f"ALTER TABLE scheduled_call ADD COLUMN {column_def};"))
                    conn.commit()
                    print(f"✓ Added column to scheduled_call table")
                except Exception as e:
                    print(f"✗ Error adding column to scheduled_call table: {e}")
        else:
            print("✓ All columns already exist in scheduled_call table")
            
    except Exception as e:
        print(f"✗ Error checking scheduled_call table: {e}")
    
    # Check session table
    try:
        result = conn.execute(text("PRAGMA table_info(session);"))
        columns = [row[1] for row in result.fetchall()]
        
        missing_columns = []
        if 'auto_activated' not in columns:
            missing_columns.append('auto_activated BOOLEAN DEFAULT 0')
        if 'reminder_sent' not in columns:
            missing_columns.append('reminder_sent BOOLEAN DEFAULT 0')
        if 'early_join_enabled' not in columns:
            missing_columns.append('early_join_enabled BOOLEAN DEFAULT 1')
        if 'buffer_minutes' not in columns:
            missing_columns.append('buffer_minutes INTEGER DEFAULT 0')
        if 'meeting_started_at' not in columns:
            missing_columns.append('meeting_started_at DATETIME')
        if 'meeting_ended_at' not in columns:
            missing_columns.append('meeting_ended_at DATETIME')
        if 'waiting_room_enabled' not in columns:
            missing_columns.append('waiting_room_enabled BOOLEAN DEFAULT 1')
        if 'calendar_event_id' not in columns:
            missing_columns.append('calendar_event_id VARCHAR(255)')
        if 'calendar_provider' not in columns:
            missing_columns.append('calendar_provider VARCHAR(50)')
        
        if missing_columns:
            print(f"Adding missing columns to session table: {missing_columns}")
            for column_def in missing_columns:
                try:
                    conn.execute(text(f"ALTER TABLE session ADD COLUMN {column_def};"))
                    conn.commit()
                    print(f"✓ Added column to session table")
                except Exception as e:
                    print(f"✗ Error adding column to session table: {e}")
        else:
            print("✓ All columns already exist in session table")
            
    except Exception as e:
        print(f"✗ Error checking session table: {e}")
    
    print("SQLite database column fixes completed!")

if __name__ == "__main__":
    fix_missing_columns()
