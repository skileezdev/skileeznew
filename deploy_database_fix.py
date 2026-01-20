#!/usr/bin/env python3
"""
Deployment script to fix production database schema
This script should be run on the production server to add missing columns
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db
from sqlalchemy import text

def deploy_database_fix():
    """Fix production database schema"""
    print("🚀 Deploying database schema fix...")
    
    try:
        with app.app_context():
            # Check database type
            db_url = str(db.engine.url)
            is_postgresql = 'postgresql' in db_url.lower()
            
            if not is_postgresql:
                print("⚠️  This script is designed for PostgreSQL production databases")
                print("📊 Current database: SQLite (local development)")
                return True
            
            print("📊 Database type: PostgreSQL (Production)")
            
            # Add message_type column to message table
            try:
                print("📝 Adding message_type column to message table...")
                db.session.execute(text("ALTER TABLE message ADD COLUMN message_type VARCHAR(20) DEFAULT 'TEXT';"))
                print("✅ Added message_type column to message table")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column name" in str(e):
                    print("ℹ️  message_type column already exists")
                else:
                    raise e
            
            # Add contract acceptance columns
            try:
                print("📝 Adding contract acceptance columns...")
                db.session.execute(text("ALTER TABLE contract ADD COLUMN accepted_at TIMESTAMP;"))
                db.session.execute(text("ALTER TABLE contract ADD COLUMN declined_at TIMESTAMP;"))
                db.session.execute(text("ALTER TABLE contract ADD COLUMN payment_completed_at TIMESTAMP;"))
                print("✅ Added contract acceptance columns")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column name" in str(e):
                    print("ℹ️  Contract acceptance columns already exist")
                else:
                    raise e
            
            # Update existing contracts to have 'pending' status
            try:
                db.session.execute(text("UPDATE contract SET status = 'pending' WHERE status = 'active';"))
                print("✅ Updated existing contracts to 'pending' status")
            except Exception as e:
                print(f"⚠️  Warning: Could not update contract status: {e}")
            
            db.session.commit()
            
        print("🎉 Production database schema fix completed successfully!")
        print("📋 Changes applied:")
        print("   - Added message_type column to message table")
        print("   - Added accepted_at, declined_at, payment_completed_at to contract table")
        print("   - Updated existing contracts to 'pending' status")
        
    except Exception as e:
        print(f"❌ Error deploying database fix: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = deploy_database_fix()
    sys.exit(0 if success else 1)
