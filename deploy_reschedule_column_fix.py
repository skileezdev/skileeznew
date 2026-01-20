#!/usr/bin/env python3
"""
Deployment script to fix the missing reschedule_proposed_time column on Render.
Run this script to add the missing column to the production database.
"""

import os
import sys
import subprocess
from datetime import datetime

def run_sql_migration():
    """Run the SQL migration to add the missing column"""
    
    print("🚀 Starting deployment fix for reschedule_proposed_time column...")
    print(f"⏰ Timestamp: {datetime.now()}")
    print("=" * 60)
    
    # Check if we're in production environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found. This script should be run in production environment.")
        return False
    
    print("✅ Production environment detected")
    print(f"📊 Database URL: {database_url[:20]}...")
    
    try:
        # Method 1: Try using Python script
        print("\n🔄 Method 1: Running Python migration script...")
        result = subprocess.run([
            sys.executable, 'add_reschedule_proposed_time_production.py'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Python migration script completed successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Python migration script failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Migration script timed out")
    except Exception as e:
        print(f"❌ Error running migration script: {str(e)}")
    
    # Method 2: Try using psql directly
    try:
        print("\n🔄 Method 2: Running SQL migration directly...")
        
        # Extract connection details from DATABASE_URL
        if database_url.startswith('postgresql://'):
            # Use psql to run the SQL file
            result = subprocess.run([
                'psql', database_url, '-f', 'add_reschedule_proposed_time.sql'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ SQL migration completed successfully")
                print(result.stdout)
                return True
            else:
                print("❌ SQL migration failed")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                
    except subprocess.TimeoutExpired:
        print("❌ SQL migration timed out")
    except FileNotFoundError:
        print("❌ psql command not found")
    except Exception as e:
        print(f"❌ Error running SQL migration: {str(e)}")
    
    # Method 3: Manual instructions
    print("\n📋 Method 3: Manual database fix required")
    print("=" * 60)
    print("If automated methods failed, please run this SQL manually:")
    print()
    print("ALTER TABLE session ADD COLUMN reschedule_proposed_time TIMESTAMP NULL;")
    print()
    print("You can run this in your database admin panel or using psql:")
    print(f"psql '{database_url}' -c \"ALTER TABLE session ADD COLUMN reschedule_proposed_time TIMESTAMP NULL;\"")
    print()
    print("After adding the column, restart your application.")
    
    return False

def verify_fix():
    """Verify that the fix was applied successfully"""
    print("\n🔍 Verifying the fix...")
    
    try:
        # Import and test the models
        from app import app
        from models import db, Session
        
        with app.app_context():
            # Try to query sessions to see if the column exists
            sessions = Session.query.limit(1).all()
            print("✅ Database query successful - column exists!")
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False

def main():
    """Main deployment function"""
    print("🚀 SKILEEZ GOL - Reschedule Column Fix Deployment")
    print("=" * 60)
    
    # Run the migration
    success = run_sql_migration()
    
    if success:
        # Verify the fix
        if verify_fix():
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("✅ The reschedule_proposed_time column has been added")
            print("✅ The reschedule approval functionality should now work")
            print("✅ No application restart required")
        else:
            print("\n⚠️  Migration completed but verification failed")
            print("🔄 Please restart the application and check again")
    else:
        print("\n❌ DEPLOYMENT FAILED!")
        print("❌ Please check the error messages above")
        print("❌ Manual intervention may be required")
        sys.exit(1)

if __name__ == '__main__':
    main()
