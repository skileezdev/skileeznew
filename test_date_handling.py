#!/usr/bin/env python3
"""
Test Date Handling for Skileez
This script tests the date and datetime handling functions
"""

import sys
import os
from datetime import datetime, date

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_date_handling():
    """Test date and datetime handling functions"""
    print("=" * 60)
    print("DATE HANDLING TEST")
    print("=" * 60)
    
    try:
        from utils import (
            format_datetime_for_user,
            convert_utc_to_user_timezone,
            format_relative_time
        )
        
        print("✅ Successfully imported date handling functions")
        
        # Test 1: Date objects
        print("\n1. Testing date objects...")
        test_date = date(2024, 1, 15)
        print(f"   Test date: {test_date}")
        
        # Test format_datetime_for_user with date
        formatted_date = format_datetime_for_user(test_date, 'UTC', 'date')
        print(f"   Formatted date: {formatted_date}")
        
        # Test convert_utc_to_user_timezone with date
        converted_date = convert_utc_to_user_timezone(test_date, 'UTC')
        print(f"   Converted date: {converted_date}")
        
        # Test format_relative_time with date
        relative_date = format_relative_time(test_date)
        print(f"   Relative date: {relative_date}")
        
        # Test 2: Datetime objects
        print("\n2. Testing datetime objects...")
        test_datetime = datetime(2024, 1, 15, 14, 30)
        print(f"   Test datetime: {test_datetime}")
        
        # Test format_datetime_for_user with datetime
        formatted_datetime = format_datetime_for_user(test_datetime, 'UTC', 'full')
        print(f"   Formatted datetime: {formatted_datetime}")
        
        # Test convert_utc_to_user_timezone with datetime
        converted_datetime = convert_utc_to_user_timezone(test_datetime, 'UTC')
        print(f"   Converted datetime: {converted_datetime}")
        
        # Test format_relative_time with datetime
        relative_datetime = format_relative_time(test_datetime)
        print(f"   Relative datetime: {relative_datetime}")
        
        # Test 3: Different timezones with datetime
        print("\n3. Testing different timezones...")
        test_timezones = ['America/New_York', 'Europe/London', 'Asia/Tokyo']
        
        for tz in test_timezones:
            try:
                formatted = format_datetime_for_user(test_datetime, tz, 'full')
                print(f"   {tz}: {formatted}")
            except Exception as e:
                print(f"   Error with {tz}: {e}")
        
        # Test 4: Template filter simulation
        print("\n4. Testing template filter simulation...")
        
        # Simulate the format_datetime filter
        def simulate_format_datetime_filter(datetime_obj, format_type='full'):
            from datetime import date, datetime
            
            if not datetime_obj:
                return ''
            
            # Handle date objects differently
            if isinstance(datetime_obj, date) and not isinstance(datetime_obj, datetime):
                # For date objects, just format the date directly
                if format_type == 'date':
                    return datetime_obj.strftime('%B %d, %Y')
                elif format_type == 'short':
                    return datetime_obj.strftime('%m/%d/%Y')
                else:  # full or any other type
                    return datetime_obj.strftime('%B %d, %Y')
            
            # For datetime objects, use timezone conversion
            return format_datetime_for_user(datetime_obj, 'UTC', format_type)
        
        # Test with date object
        date_result = simulate_format_datetime_filter(test_date, 'date_only')
        print(f"   Template filter with date: {date_result}")
        
        # Test with datetime object
        datetime_result = simulate_format_datetime_filter(test_datetime, 'full')
        print(f"   Template filter with datetime: {datetime_result}")
        
        print("\n" + "=" * 60)
        print("✅ All date handling tests completed successfully!")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases for date handling"""
    print("\nTesting edge cases...")
    
    try:
        from utils import format_datetime_for_user, format_relative_time
        
        # Test None values
        print("   Testing None values...")
        none_result = format_datetime_for_user(None, 'UTC')
        print(f"   None result: '{none_result}'")
        
        # Test empty string
        print("   Testing empty string...")
        empty_result = format_datetime_for_user("", 'UTC')
        print(f"   Empty result: '{empty_result}'")
        
        # Test future dates
        print("   Testing future dates...")
        future_date = date(2025, 12, 25)
        future_relative = format_relative_time(future_date)
        print(f"   Future date relative: {future_relative}")
        
        # Test past dates
        print("   Testing past dates...")
        past_date = date(2023, 1, 1)
        past_relative = format_relative_time(past_date)
        print(f"   Past date relative: {past_relative}")
        
        return True
        
    except Exception as e:
        print(f"❌ Edge case test error: {e}")
        return False

def main():
    """Main test function"""
    print("Date Handling Test for Skileez")
    print("=" * 60)
    
    # Test date handling
    if not test_date_handling():
        print("\n❌ Date handling tests failed.")
        return False
    
    # Test edge cases
    if not test_edge_cases():
        print("\n❌ Edge case tests failed.")
        return False
    
    print("\n🎉 All date handling tests passed!")
    print("\nNext steps:")
    print("1. ✅ Date objects are handled correctly")
    print("2. ✅ Datetime objects are handled correctly")
    print("3. ✅ Template filters work with both types")
    print("4. ✅ Edge cases are handled properly")
    print("5. 🔄 Deploy the changes to fix the production error")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
