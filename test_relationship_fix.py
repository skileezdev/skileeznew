#!/usr/bin/env python3
"""
Test script to verify session-contract relationship fix
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_session_contract_relationship():
    """Test the session-contract relationship"""
    try:
        from app import app, db
        from models import Session, Proposal, Contract, User
        
        with app.app_context():
            print("🧪 Testing session-contract relationship...")
            
            # Check what data exists
            session_count = Session.query.count()
            proposal_count = Proposal.query.count()
            contract_count = Contract.query.count()
            user_count = User.query.count()
            
            print(f"📊 Database stats:")
            print(f"   Users: {user_count}")
            print(f"   Sessions: {session_count}")
            print(f"   Proposals: {proposal_count}")
            print(f"   Contracts: {contract_count}")
            
            if session_count == 0:
                print("❌ No sessions found in database")
                return False
            
            if contract_count == 0:
                print("❌ No contracts found in database")
                return False
            
            # Get a session
            session = Session.query.first()
            print(f"✅ Found session {session.id}")
            print(f"   Proposal ID: {session.proposal_id}")
            
            # Test the relationship
            contract = session.get_contract()
            
            if contract is None:
                print("❌ session.get_contract() returned None")
                return False
            
            print(f"✅ session.get_contract() returned contract {contract.id}")
            print(f"   Contract number: {contract.contract_number}")
            
            # Test direct access
            if hasattr(session.proposal, 'contract'):
                direct_contract = session.proposal.contract
                print(f"✅ session.proposal.contract exists: {direct_contract.id if direct_contract else 'None'}")
            else:
                print("❌ session.proposal.contract does not exist")
                return False
            
            print("✅ All relationship tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting session-contract relationship test...")
    
    if test_session_contract_relationship():
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
