#!/usr/bin/env python3
"""
Quick fix script for the missing reschedule_proposed_time column.
Run this on Render to fix the database issue immediately.
"""

import os
from sqlalchemy import create_engine, text

def quick_fix():
    """Quick fix for the missing column"""
    print("🚨 QUICK FIX: Adding reschedule_proposed_time column")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'session' AND column_name = 'reschedule_proposed_time'
            """))
            
            if result.fetchone():
                print("✅ Column already exists")
                return True
            
            # Add the column
            conn.execute(text("""
                ALTER TABLE session 
                ADD COLUMN reschedule_proposed_time TIMESTAMP NULL
            """))
            conn.commit()
            
            print("✅ Column added successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    quick_fix()
