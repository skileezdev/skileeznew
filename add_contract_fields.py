#!/usr/bin/env python3
"""
Script to manually add contract acceptance fields to the database
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db
from sqlalchemy import text

def add_contract_fields():
    """Add new fields to contract and message tables"""
    print("🔄 Adding contract acceptance fields to database...")
    
    try:
        with app.app_context():
            # Add new columns to contract table
            db.session.execute(text("ALTER TABLE contract ADD COLUMN accepted_at DATETIME;"))
            print("✅ Added accepted_at column to contract table")
            
            db.session.execute(text("ALTER TABLE contract ADD COLUMN declined_at DATETIME;"))
            print("✅ Added declined_at column to contract table")
            
            db.session.execute(text("ALTER TABLE contract ADD COLUMN payment_completed_at DATETIME;"))
            print("✅ Added payment_completed_at column to contract table")
            
            # Add message_type column to message table
            db.session.execute(text("ALTER TABLE message ADD COLUMN message_type VARCHAR(20) DEFAULT 'TEXT';"))
            print("✅ Added message_type column to message table")
            
            # Update existing contracts to have 'pending' status
            db.session.execute(text("UPDATE contract SET status = 'pending' WHERE status = 'active';"))
            print("✅ Updated existing contracts to 'pending' status")
            
            db.session.commit()
            
        print("🎉 All fields added successfully!")
        
    except Exception as e:
        print(f"❌ Error adding fields: {e}")
        # Check if columns already exist
        if "duplicate column name" in str(e):
            print("ℹ️  Some columns may already exist. This is normal if the migration was partially run.")
        return False
    
    return True

if __name__ == "__main__":
    add_contract_fields()
