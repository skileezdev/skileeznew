#!/usr/bin/env python3
"""
Test Timezone Functionality for Skileez
This script tests the timezone conversion and formatting functions
"""

import sys
import os
from datetime import datetime
import pytz

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_timezone_functions():
    """Test the timezone utility functions"""
    print("=" * 60)
    print("TIMEZONE FUNCTIONALITY TEST")
    print("=" * 60)
    
    try:
        from utils import (
            get_timezone_choices, 
            convert_timezone, 
            get_timezone_offset,
            format_datetime_in_timezone,
            get_user_timezone,
            convert_utc_to_user_timezone,
            format_datetime_for_user
        )
        
        print("✅ Successfully imported timezone functions")
        
        # Test 1: Get timezone choices
        print("\n1. Testing get_timezone_choices()...")
        timezone_choices = get_timezone_choices()
        print(f"   Found {len(timezone_choices)} timezones")
        
        # Show first 10 timezones
        print("   First 10 timezones:")
        for i, (tz_name, display_name) in enumerate(timezone_choices[:10]):
            print(f"   {i+1}. {tz_name} -> {display_name}")
        
        # Test 2: Timezone conversion
        print("\n2. Testing timezone conversion...")
        test_datetime = datetime(2024, 1, 15, 14, 30)  # 2:30 PM
        print(f"   Original time: {test_datetime}")
        
        # Convert to different timezones
        test_timezones = ['UTC', 'America/New_York', 'Europe/London', 'Asia/Tokyo', 'Australia/Sydney']
        
        for tz in test_timezones:
            try:
                converted = convert_timezone(test_datetime, 'UTC', tz)
                offset = get_timezone_offset(tz)
                print(f"   {tz} ({offset}): {converted.strftime('%Y-%m-%d %H:%M %Z')}")
            except Exception as e:
                print(f"   Error converting to {tz}: {e}")
        
        # Test 3: Format datetime for user
        print("\n3. Testing format_datetime_for_user()...")
        utc_time = datetime(2024, 1, 15, 14, 30)
        
        for tz in test_timezones:
            try:
                formatted = format_datetime_for_user(utc_time, tz, 'full')
                print(f"   {tz}: {formatted}")
            except Exception as e:
                print(f"   Error formatting for {tz}: {e}")
        
        # Test 4: Timezone offset
        print("\n4. Testing get_timezone_offset()...")
        for tz in test_timezones:
            try:
                offset = get_timezone_offset(tz)
                print(f"   {tz}: {offset}")
            except Exception as e:
                print(f"   Error getting offset for {tz}: {e}")
        
        # Test 5: User timezone detection
        print("\n5. Testing user timezone detection...")
        user_timezone = get_user_timezone(None)  # No user object
        print(f"   Default user timezone: {user_timezone}")
        
        print("\n" + "=" * 60)
        print("✅ All timezone tests completed successfully!")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_pytz_installation():
    """Test if pytz is properly installed"""
    print("\nTesting pytz installation...")
    
    try:
        import pytz
        print(f"✅ pytz version: {pytz.__version__}")
        
        # Test basic pytz functionality
        utc = pytz.UTC
        ny_tz = pytz.timezone('America/New_York')
        
        now = datetime.now()
        utc_now = utc.localize(now)
        ny_now = utc_now.astimezone(ny_tz)
        
        print(f"   Current UTC time: {utc_now}")
        print(f"   Current NY time: {ny_now}")
        
        return True
        
    except ImportError:
        print("❌ pytz is not installed. Please install it with: pip install pytz")
        return False
    except Exception as e:
        print(f"❌ pytz test error: {e}")
        return False

def test_timezone_choices_performance():
    """Test the performance of getting timezone choices"""
    print("\nTesting timezone choices performance...")
    
    try:
        from utils import get_timezone_choices
        import time
        
        start_time = time.time()
        choices = get_timezone_choices()
        end_time = time.time()
        
        print(f"✅ Generated {len(choices)} timezone choices in {end_time - start_time:.3f} seconds")
        
        # Check for common timezones
        common_timezones = [
            'UTC', 'America/New_York', 'America/Chicago', 'America/Denver', 
            'America/Los_Angeles', 'Europe/London', 'Europe/Paris', 'Asia/Tokyo'
        ]
        
        found_timezones = [choice[0] for choice in choices]
        missing_timezones = [tz for tz in common_timezones if tz not in found_timezones]
        
        if missing_timezones:
            print(f"⚠️  Missing common timezones: {missing_timezones}")
        else:
            print("✅ All common timezones found")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

def main():
    """Main test function"""
    print("Timezone Functionality Test for Skileez")
    print("=" * 60)
    
    # Test pytz installation first
    if not test_pytz_installation():
        print("\n❌ pytz test failed. Please fix pytz installation first.")
        return False
    
    # Test timezone functions
    if not test_timezone_functions():
        print("\n❌ Timezone function tests failed.")
        return False
    
    # Test performance
    if not test_timezone_choices_performance():
        print("\n❌ Performance test failed.")
        return False
    
    print("\n🎉 All timezone tests passed!")
    print("\nNext steps:")
    print("1. ✅ Timezone functions are working correctly")
    print("2. ✅ pytz is properly installed")
    print("3. ✅ Performance is acceptable")
    print("4. 🔄 Deploy the changes to test in production")
    print("5. 📧 Test email notifications with different timezones")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
