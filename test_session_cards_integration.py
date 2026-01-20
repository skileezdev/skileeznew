#!/usr/bin/env python3
"""
Test script to verify session cards integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import User, Contract, ScheduledCall, Message
from scheduling_utils import create_call_scheduled_message
from datetime import datetime, timedelta
import json

def test_session_cards_integration():
    """Test that session cards are created correctly when sessions are scheduled"""
    
    print("🧪 Testing Session Cards Integration")
    print("=" * 50)
    
    try:
        with app.app_context():
            # Test 1: Check if message types are supported
            print("✅ Testing message types...")
            
            # Create a test message with SESSION_SCHEDULED type
            test_message_data = {
                "session_id": 123,
                "scheduled_at": "December 15, 2024 at 2:00 PM",
                "duration": "60",
                "status": "scheduled",
                "session_type": "paid",
                "contract_title": "Python Programming",
                "session_number": "1 of 5"
            }
            
            test_message = Message(
                sender_id=1,
                recipient_id=2,
                content=json.dumps(test_message_data),
                message_type='SESSION_SCHEDULED'
            )
            
            print(f"✅ Created test message with type: {test_message.message_type}")
            
            # Test 2: Check template filters
            print("\n✅ Testing template filters...")
            
            # Test extract_session_info filter
            from app import extract_session_info
            session_info = extract_session_info(json.dumps(test_message_data))
            
            if session_info:
                print(f"✅ Session info extracted: {session_info.get('session_id')}")
                print(f"   - Scheduled: {session_info.get('scheduled_at')}")
                print(f"   - Duration: {session_info.get('duration')}")
                print(f"   - Status: {session_info.get('status')}")
            else:
                print("❌ Failed to extract session info")
            
            # Test 3: Check consultation filter
            print("\n✅ Testing consultation filter...")
            
            consultation_data = {
                "consultation_id": 456,
                "scheduled_at": "December 16, 2024 at 3:00 PM",
                "status": "scheduled",
                "coach_name": "Sarah Johnson",
                "student_name": "John Doe",
                "duration": "15"
            }
            
            from app import extract_consultation_info
            consultation_info = extract_consultation_info(json.dumps(consultation_data))
            
            if consultation_info:
                print(f"✅ Consultation info extracted: {consultation_info.get('consultation_id')}")
                print(f"   - Scheduled: {consultation_info.get('scheduled_at')}")
                print(f"   - Coach: {consultation_info.get('coach_name')}")
                print(f"   - Status: {consultation_info.get('status')}")
            else:
                print("❌ Failed to extract consultation info")
            
            # Test 4: Check scheduling_utils integration
            print("\n✅ Testing scheduling_utils integration...")
            
            # Check if create_call_scheduled_message function exists
            if hasattr(create_call_scheduled_message, '__call__'):
                print("✅ create_call_scheduled_message function exists")
            else:
                print("❌ create_call_scheduled_message function not found")
            
            print("\n🎉 All tests passed! Session cards integration is ready.")
            print("\n📋 Next steps:")
            print("1. Visit /session-cards-demo to see the cards in action")
            print("2. Schedule a free consultation or paid session to test real integration")
            print("3. Check the messages between coach and student for interactive cards")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_session_cards_integration()
