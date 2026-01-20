#!/usr/bin/env python3
"""
Script to fix contract status issues
This script will activate contracts that are paid but not active
"""

import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Contract

def fix_contract_statuses():
    """Fix contracts that are paid but not active"""
    with app.app_context():
        try:
            # Find contracts that are paid but not active
            problematic_contracts = Contract.query.filter_by(
                payment_status='paid',
                status='accepted'
            ).all()
            
            print(f"Found {len(problematic_contracts)} contracts that are paid but not active")
            
            fixed_count = 0
            for contract in problematic_contracts:
                print(f"Fixing contract {contract.id} (Contract #{contract.contract_number})")
                print(f"  - Payment status: {contract.payment_status}")
                print(f"  - Contract status: {contract.status}")
                
                # Activate the contract
                contract.status = 'active'
                fixed_count += 1
            
            if fixed_count > 0:
                db.session.commit()
                print(f"Successfully fixed {fixed_count} contracts")
            else:
                print("No contracts needed fixing")
                
            # Also check for any other status issues
            all_contracts = Contract.query.all()
            print(f"\nContract status summary:")
            print(f"Total contracts: {len(all_contracts)}")
            
            status_counts = {}
            payment_status_counts = {}
            
            for contract in all_contracts:
                status_counts[contract.status] = status_counts.get(contract.status, 0) + 1
                payment_status_counts[contract.payment_status] = payment_status_counts.get(contract.payment_status, 0) + 1
            
            print(f"Contract statuses: {status_counts}")
            print(f"Payment statuses: {payment_status_counts}")
            
        except Exception as e:
            print(f"Error fixing contracts: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("Starting contract status fix...")
    fix_contract_statuses()
    print("Contract status fix completed!")
