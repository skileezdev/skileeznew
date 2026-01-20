#!/usr/bin/env python3
"""
Test script to check message rendering and timezone handling
"""

from app import app
from models import Message, User
from datetime import datetime, timezone
import pytz

def test_message_rendering():
    """Test how messages are being rendered"""
    
    with app.app_context():
        # Get the most recent messages
        messages = Message.query.order_by(Message.created_at.desc()).limit(5).all()
        
        print("=== MESSAGE RENDERING TEST ===")
        print()
        
        for i, message in enumerate(messages):
            print(f"Message {i+1}:")
            print(f"  ID: {message.id}")
            print(f"  Content: {message.content[:50]}...")
            print(f"  Created at (raw): {message.created_at}")
            print(f"  Created at (iso): {message.created_at.isoformat()}")
            print(f"  Created at (strftime): {message.created_at.strftime('%H:%M')}")
            
            # Test timezone conversion
            dubai_tz = pytz.timezone('Asia/Dubai')
            dubai_time = message.created_at.astimezone(dubai_tz)
            print(f"  Dubai time: {dubai_time}")
            print(f"  Dubai time (formatted): {dubai_time.strftime('%I:%M %p')}")
            print()
        
        print("=== EXPECTED HTML OUTPUT ===")
        print("Each message should have:")
        print('  <span class="message-timestamp" data-utc-time="2025-08-19T10:00:00+00:00">')
        print("  <!-- This will be replaced by JavaScript -->")
        print("  10:00")
        print("  </span>")
        print()
        print("=== CLIENT-SIDE CONVERSION ===")
        print("JavaScript should convert 10:00 UTC to 2:00 PM Dubai time")

if __name__ == "__main__":
    test_message_rendering()
