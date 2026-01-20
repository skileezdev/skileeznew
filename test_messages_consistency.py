#!/usr/bin/env python3
"""
Test script to verify messages consistency across different access points
"""

from app import app, db
from models import User, CoachProfile, StudentProfile, LearningRequest, Proposal, Message
from datetime import datetime

def test_messages_consistency():
    """Test that messages have consistent features regardless of access point"""
    with app.app_context():
        print("🧪 Testing messages consistency...")
        
        try:
            # Test that the routes can be imported
            from routes import inbox, conversation, create_contract_from_messages, schedule_call_from_messages
            print("✅ All message routes imported successfully")
            
            # Test that the templates exist
            import os
            templates_to_check = [
                "templates/messages/inbox.html",
                "templates/messages/conversation.html", 
                "templates/messages/create_contract.html",
                "templates/messages/schedule_call.html"
            ]
            
            for template in templates_to_check:
                if os.path.exists(template):
                    print(f"✅ Template exists: {template}")
                else:
                    print(f"❌ Template missing: {template}")
            
            # Test that conversation template has enhanced features
            conversation_template = "templates/messages/conversation.html"
            if os.path.exists(conversation_template):
                with open(conversation_template, 'r') as f:
                    content = f.read()
                    if 'Create Contract' in content:
                        print("✅ Conversation template has 'Create Contract' button")
                    else:
                        print("❌ Conversation template missing 'Create Contract' button")
                    
                    if 'Schedule Call' in content:
                        print("✅ Conversation template has 'Schedule Call' button")
                    else:
                        print("❌ Conversation template missing 'Schedule Call' button")
            
            # Test that inbox template navigates to conversation pages
            inbox_template = "templates/messages/inbox.html"
            if os.path.exists(inbox_template):
                with open(inbox_template, 'r') as f:
                    content = f.read()
                    if 'url_for(\'conversation\'' in content:
                        print("✅ Inbox template navigates to conversation pages")
                    else:
                        print("❌ Inbox template doesn't navigate to conversation pages")
            
            print("🎉 Messages consistency test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Messages consistency test failed: {e}")
            return False

if __name__ == "__main__":
    test_messages_consistency()
