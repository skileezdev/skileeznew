#!/usr/bin/env python3
"""
Script to run the new migration for contract acceptance fields
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db
from alembic import command
from alembic.config import Config

def run_migration():
    """Run the new migration"""
    print("🔄 Running migration for contract acceptance fields...")
    
    try:
        # Create Alembic configuration
        alembic_cfg = Config("migrations/alembic.ini")
        alembic_cfg.set_main_option("script_location", "migrations")
        
        # Run the migration
        with app.app_context():
            command.upgrade(alembic_cfg, "006")
        
        print("✅ Migration completed successfully!")
        print("📝 Added fields:")
        print("   - contract.accepted_at")
        print("   - contract.declined_at") 
        print("   - contract.payment_completed_at")
        print("   - message.message_type")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    run_migration()
