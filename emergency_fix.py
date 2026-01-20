#!/usr/bin/env python3
"""
Emergency fix for the reschedule_proposed_time column issue.
This script will definitely add the missing column to fix the 500 errors.
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def emergency_fix():
    """Emergency fix for the missing reschedule_proposed_time column"""
    
    print("🚨 EMERGENCY FIX: Adding reschedule_proposed_time column")
    print("=" * 60)
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found!")
        print("Available environment variables:")
        for key in sorted(os.environ.keys()):
            if 'DATABASE' in key.upper() or 'POSTGRES' in key.upper():
                print(f"  {key}: {os.environ[key][:50]}...")
        return False
    
    print(f"✅ Found DATABASE_URL: {database_url[:30]}...")
    
    try:
        # Fix postgres:// to postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
            print("✅ Fixed postgres:// URL format")
        
        # Connect to database
        print("🔄 Connecting to database...")
        conn = psycopg2.connect(database_url)
        conn.autocommit = True  # Enable autocommit for DDL operations
        cursor = conn.cursor()
        
        print("✅ Connected to database successfully")
        
        # Check if column exists
        print("🔍 Checking if reschedule_proposed_time column exists...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'session' 
            AND column_name = 'reschedule_proposed_time'
        """)
        
        result = cursor.fetchone()
        if result:
            print("✅ Column 'reschedule_proposed_time' already exists!")
            cursor.close()
            conn.close()
            return True
        
        print("❌ Column does not exist - adding it now...")
        
        # Add the column
        print("🔄 Adding reschedule_proposed_time column...")
        cursor.execute("""
            ALTER TABLE session 
            ADD COLUMN reschedule_proposed_time TIMESTAMP NULL
        """)
        
        print("✅ Column added successfully!")
        
        # Verify the column was added
        print("🔍 Verifying column addition...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'session' 
            AND column_name = 'reschedule_proposed_time'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"✅ Verification successful: {result}")
        else:
            print("❌ Verification failed!")
            return False
        
        cursor.close()
        conn.close()
        
        print("🎉 EMERGENCY FIX COMPLETED SUCCESSFULLY!")
        print("The 500 errors should now be resolved.")
        return True
        
    except Exception as e:
        print(f"❌ Emergency fix failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = emergency_fix()
    if not success:
        print("\n💥 EMERGENCY FIX FAILED!")
        sys.exit(1)
    else:
        print("\n✅ EMERGENCY FIX SUCCESSFUL!")
        print("Your app should now work without 500 errors.")
