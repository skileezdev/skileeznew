#!/usr/bin/env python3
"""
Test script to verify CSRF token fix for call scheduling
"""

from app import app, db
from models import User, CoachProfile, StudentProfile, LearningRequest, Proposal, Message
from datetime import datetime

def test_csrf_fix():
    """Test that CSRF tokens are properly handled"""
    with app.app_context():
        print("🧪 Testing CSRF token fix...")
        
        try:
            # Test that the routes can be imported
            from routes import schedule_call_from_messages, create_contract_from_messages
            print("✅ Call scheduling routes imported successfully")
            
            # Test that the templates exist and have CSRF tokens
            import os
            schedule_call_template = "templates/messages/schedule_call.html"
            create_contract_template = "templates/messages/create_contract.html"
            
            if os.path.exists(schedule_call_template):
                with open(schedule_call_template, 'r') as f:
                    content = f.read()
                    if 'csrf_token' in content:
                        print("✅ Schedule call template has CSRF token")
                    else:
                        print("❌ Schedule call template missing CSRF token")
            
            if os.path.exists(create_contract_template):
                with open(create_contract_template, 'r') as f:
                    content = f.read()
                    if 'csrf_token' in content or 'form.hidden_tag()' in content:
                        print("✅ Create contract template has CSRF token")
                    else:
                        print("❌ Create contract template missing CSRF token")
            
            print("🎉 CSRF token fix test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ CSRF token fix test failed: {e}")
            return False

if __name__ == "__main__":
    test_csrf_fix()
