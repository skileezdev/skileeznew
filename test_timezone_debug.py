#!/usr/bin/env python3
"""
Debug script to test timezone handling in the messaging system
"""

from datetime import datetime, timezone
import pytz

def test_timezone_handling():
    """Test timezone conversion and display"""
    
    print("=== TIMEZONE DEBUG TEST ===")
    print()
    
    # Test server time
    utc_now = datetime.now(timezone.utc)
    local_now = datetime.now()
    
    print(f"UTC time: {utc_now}")
    print(f"Local time: {local_now}")
    print(f"Timezone offset: {(local_now - utc_now.replace(tzinfo=None)).total_seconds() / 3600:.1f} hours")
    print()
    
    # Test Dubai timezone
    dubai_tz = pytz.timezone('Asia/Dubai')
    dubai_time = utc_now.astimezone(dubai_tz)
    
    print(f"UTC time: {utc_now}")
    print(f"Dubai time: {dubai_time}")
    print(f"Difference: {(dubai_time - utc_now).total_seconds() / 3600:.1f} hours")
    print()
    
    # Test client-side conversion simulation
    print("=== CLIENT-SIDE CONVERSION SIMULATION ===")
    
    # Simulate a message sent at 2:00 PM Dubai time
    dubai_2pm = dubai_tz.localize(datetime.now().replace(hour=14, minute=0, second=0, microsecond=0))
    utc_2pm = dubai_2pm.astimezone(timezone.utc)
    
    print(f"Message sent at 2:00 PM Dubai time")
    print(f"Stored in database as UTC: {utc_2pm}")
    print()
    
    # Simulate client-side conversion back to Dubai time
    client_dubai_time = utc_2pm.astimezone(dubai_tz)
    print(f"Client converts back to Dubai time: {client_dubai_time}")
    print()
    
    # Test the JavaScript conversion logic
    print("=== JAVASCRIPT CONVERSION SIMULATION ===")
    
    # Simulate what JavaScript would do
    utc_iso = utc_2pm.isoformat()
    print(f"UTC ISO string sent to client: {utc_iso}")
    
    # Simulate JavaScript Date object
    js_date = datetime.fromisoformat(utc_iso.replace('Z', '+00:00'))
    print(f"JavaScript Date object: {js_date}")
    
    # Simulate toLocaleTimeString
    print(f"JavaScript toLocaleTimeString: {js_date.strftime('%I:%M %p')}")
    print()
    
    print("=== EXPECTED BEHAVIOR ===")
    print("1. Server stores all times in UTC")
    print("2. Client receives UTC ISO strings")
    print("3. Client converts to local timezone")
    print("4. Both sender and receiver see times in their local timezone")
    print()
    
    print("=== CURRENT ISSUE ===")
    print("The 4-hour difference suggests the client-side conversion")
    print("isn't working properly or there's a mismatch in the UTC storage.")

if __name__ == "__main__":
    test_timezone_handling()
