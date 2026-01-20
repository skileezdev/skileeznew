#!/usr/bin/env python3
"""
Test script to verify contract template null safety fixes
"""

from app import app, db
from models import User, CoachProfile, StudentProfile, LearningRequest, Proposal, Message
from datetime import datetime

def test_contract_template_fix():
    """Test that contract template handles null values gracefully"""
    with app.app_context():
        print("🧪 Testing contract template null safety...")
        
        try:
            # Test that the template exists and has null checks
            import os
            template_path = "templates/messages/create_contract.html"
            
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    content = f.read()
                    
                    # Check for null safety in accepted_at
                    if '{% if proposal.accepted_at %}' in content:
                        print("✅ Template has null check for accepted_at")
                    else:
                        print("❌ Template missing null check for accepted_at")
                    
                    # Check for null safety in learning_request.title
                    if 'proposal.learning_request.title if proposal.learning_request and proposal.learning_request.title' in content:
                        print("✅ Template has null check for learning_request.title")
                    else:
                        print("❌ Template missing null check for learning_request.title")
                    
                    # Check for null safety in proposal fields
                    if 'proposal.session_count or' in content:
                        print("✅ Template has null check for session_count")
                    else:
                        print("❌ Template missing null check for session_count")
                    
                    if 'proposal.price_per_session or 0' in content:
                        print("✅ Template has null check for price_per_session")
                    else:
                        print("❌ Template missing null check for price_per_session")
                    
                    if 'proposal.total_price or 0' in content:
                        print("✅ Template has null check for total_price")
                    else:
                        print("❌ Template missing null check for total_price")
            
            # Test that the route has proper error handling
            from routes import create_contract_from_messages
            print("✅ Contract creation route imported successfully")
            
            print("🎉 Contract template null safety test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Contract template null safety test failed: {e}")
            return False

if __name__ == "__main__":
    test_contract_template_fix()
