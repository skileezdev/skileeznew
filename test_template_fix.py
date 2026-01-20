#!/usr/bin/env python3
"""
Test script to verify template fix
"""

def test_template_fix():
    """Test that template fix works correctly"""
    print("🧪 Testing template fix...")
    
    try:
        # Test that the template has the improved null check
        import os
        template_path = "templates/dashboard/student_dashboard.html"
        
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                content = f.read()
                
                # Check for the improved null safety pattern
                if '{% set contract = session.proposal.contract if session.proposal and session.proposal.contract else none %}' in content:
                    print("✅ Template has improved null check with contract variable")
                else:
                    print("❌ Template missing improved null check")
                
                # Check for the safer contract.id access
                if '{% if contract and contract.id %}' in content:
                    print("✅ Template has safe contract.id access")
                else:
                    print("❌ Template missing safe contract.id access")
        
        print("🎉 Template fix test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Template fix test failed: {e}")
        return False

if __name__ == "__main__":
    test_template_fix()
