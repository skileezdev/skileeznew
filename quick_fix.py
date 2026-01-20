#!/usr/bin/env python3
"""
Quick fix script to add the missing reschedule_proposed_time column.
Run this directly on Render to fix the 500 errors immediately.
"""

import os
import psycopg2

def quick_fix():
    """Quick fix for the missing column"""
    print("🚨 QUICK FIX: Adding reschedule_proposed_time column")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ No DATABASE_URL found")
        return False
    
    try:
        # Fix postgres:// URL
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        # Connect and add column
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("""
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'session' AND column_name = 'reschedule_proposed_time'
        """)
        
        if cursor.fetchone():
            print("✅ Column already exists")
        else:
            # Add the column
            cursor.execute("""
                ALTER TABLE session 
                ADD COLUMN reschedule_proposed_time TIMESTAMP NULL
            """)
            print("✅ Column added successfully")
        
        cursor.close()
        conn.close()
        print("🎉 QUICK FIX COMPLETED!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    quick_fix()
