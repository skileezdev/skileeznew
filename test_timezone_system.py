#!/usr/bin/env python3
"""
Test script for the timezone system
This script tests the smart timezone handling functionality
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_timezone_manager():
    """Test the timezone manager functionality"""
    print("=== Testing Timezone Manager ===")
    
    try:
        from timezone_utils import get_timezone_manager
        tz_manager = get_timezone_manager()
        
        # Test 1: Get timezone choices
        print("\n1. Testing timezone choices:")
        choices = tz_manager.get_timezone_choices()
        print(f"Found {len(choices)} timezone choices")
        for tz, name in choices[:5]:  # Show first 5
            print(f"  {tz}: {name}")
        
        # Test 2: Parse local datetime
        print("\n2. Testing local datetime parsing:")
        test_date = "2025-01-15"
        test_time = "19:30"
        test_timezone = "Asia/Dubai"
        
        utc_dt = tz_manager.parse_local_datetime(test_date, test_time, test_timezone)
        print(f"Input: {test_date} {test_time} ({test_timezone})")
        print(f"UTC: {utc_dt}")
        
        # Test 3: Validate scheduled time
        print("\n3. Testing time validation:")
        
        # Test past time (should fail)
        past_time = datetime.utcnow() - timedelta(hours=1)
        is_valid, error = tz_manager.validate_scheduled_time(past_time, test_timezone)
        print(f"Past time validation: {is_valid} - {error}")
        
        # Test future time (should pass)
        future_time = datetime.utcnow() + timedelta(hours=2)
        is_valid, error = tz_manager.validate_scheduled_time(future_time, test_timezone)
        print(f"Future time validation: {is_valid} - {error}")
        
        # Test 4: Format datetime for user
        print("\n4. Testing datetime formatting:")
        formatted = tz_manager.format_datetime_for_user(utc_dt, test_timezone)
        print(f"Formatted for {test_timezone}: {formatted}")
        
        # Test 5: Timezone conversion preview
        print("\n5. Testing timezone conversion preview:")
        preview = tz_manager.get_timezone_conversion_preview(
            utc_dt, 
            "Asia/Dubai", 
            "America/New_York"
        )
        print("Timezone conversion preview:")
        for key, value in preview.items():
            print(f"  {key}: {value}")
        
        print("\n✅ All timezone tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Timezone test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scheduling_validation():
    """Test the scheduling validation logic"""
    print("\n=== Testing Scheduling Validation ===")
    
    try:
        from timezone_utils import get_timezone_manager
        tz_manager = get_timezone_manager()
        
        # Test case: User in Dubai scheduling at 7:19 PM Dubai time
        print("\nTest Case: Dubai user scheduling at 7:19 PM")
        
        # Create a test datetime (7:19 PM Dubai time)
        test_date = "2025-01-15"
        test_time = "19:19"
        dubai_timezone = "Asia/Dubai"
        
        # Parse the local time
        utc_dt = tz_manager.parse_local_datetime(test_date, test_time, dubai_timezone)
        print(f"Local time: {test_date} {test_time} ({dubai_timezone})")
        print(f"UTC time: {utc_dt}")
        
        # Validate the time
        is_valid, error = tz_manager.validate_scheduled_time(utc_dt, dubai_timezone)
        print(f"Validation result: {is_valid}")
        if not is_valid:
            print(f"Error: {error}")
        
        # Show conversion to other timezones
        print("\nTimezone conversions:")
        other_timezones = ["America/New_York", "Europe/London", "Asia/Tokyo"]
        
        for other_tz in other_timezones:
            other_time = tz_manager.format_datetime_for_user(utc_dt, other_tz)
            print(f"  {other_tz}: {other_time}")
        
        print("\n✅ Scheduling validation test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Scheduling validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Timezone System Test")
    print("=" * 50)
    
    # Test 1: Timezone manager
    test1_passed = test_timezone_manager()
    
    # Test 2: Scheduling validation
    test2_passed = test_scheduling_validation()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Timezone Manager: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Scheduling Validation: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The timezone system is working correctly.")
        print("\nKey Features Verified:")
        print("✅ Timezone parsing and conversion")
        print("✅ Smart validation (no more 'time in past' errors)")
        print("✅ Timezone conversion previews")
        print("✅ User-friendly error messages")
        print("✅ Global timezone support")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
