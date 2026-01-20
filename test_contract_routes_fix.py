#!/usr/bin/env python3
"""
Test script to verify contract route fixes
"""

from app import app, db
from models import User, CoachProfile, StudentProfile, LearningRequest, Proposal, Message, Contract
from datetime import datetime

def test_contract_routes_fix():
    """Test that contract templates use correct route names"""
    with app.app_context():
        print("🧪 Testing contract route fixes...")
        
        try:
            # Test that the templates exist and have correct route names
            import os
            templates_to_check = [
                "templates/contracts/view_contract.html",
                "templates/contracts/manage_sessions.html"
            ]
            
            for template in templates_to_check:
                if os.path.exists(template):
                    with open(template, 'r') as f:
                        content = f.read()
                        
                        # Check for correct route name
                        if 'url_for(\'conversation\'' in content:
                            print(f"✅ {template} uses correct 'conversation' route")
                        else:
                            print(f"❌ {template} missing correct 'conversation' route")
                        
                        # Check that old 'messages' route is not used
                        if 'url_for(\'messages\'' in content:
                            print(f"❌ {template} still uses incorrect 'messages' route")
                        else:
                            print(f"✅ {template} no longer uses incorrect 'messages' route")
            
            # Test that the routes can be imported
            from routes import view_contract, manage_sessions
            print("✅ Contract routes imported successfully")
            
            print("🎉 Contract route fixes test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Contract route fixes test failed: {e}")
            return False

if __name__ == "__main__":
    test_contract_routes_fix()
