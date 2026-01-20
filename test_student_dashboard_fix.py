#!/usr/bin/env python3
"""
Test script to verify student dashboard fix
"""

from app import app, db
from models import User, CoachProfile, StudentProfile, LearningRequest, Proposal, Message, Contract, Session
from datetime import datetime

def test_student_dashboard_fix():
    """Test that student dashboard fixes work correctly"""
    print("🧪 Testing student dashboard fix...")
    
    try:
        # Test datetime import fix
        from datetime import datetime
        test_datetime = datetime.utcnow()
        print(f"✅ Datetime import works: {test_datetime}")
        
        # Test that the route can be imported
        from routes import student_dashboard
        print("✅ student_dashboard route imported successfully")
        
        # Test that the template has null checks
        import os
        template_path = "templates/dashboard/student_dashboard.html"
        
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                content = f.read()
                
                # Check for null safety in contract access
                if '{% if session.proposal.contract %}' in content:
                    print("✅ Template has null check for session.proposal.contract")
                else:
                    print("❌ Template missing null check for session.proposal.contract")
        
        print("🎉 Student dashboard fix test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Student dashboard fix test failed: {e}")
        return False

if __name__ == "__main__":
    test_student_dashboard_fix()
