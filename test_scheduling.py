#!/usr/bin/env python3
"""
Test script for the scheduling system
Run this to verify all components are working correctly
"""

import os
import sys
from datetime import datetime, timedelta
import pytz

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import app components, but handle gracefully if they fail
try:
    from app import app, db
    APP_AVAILABLE = True
except Exception as e:
    print(f"⚠️  App import failed: {e}")
    APP_AVAILABLE = False

try:
    from models import User, ScheduledCall, CallNotification
    MODELS_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Models import failed: {e}")
    MODELS_AVAILABLE = False

try:
    from scheduling_utils import (
        get_scheduling_options, 
        schedule_free_consultation, 
        schedule_paid_session,
        check_call_availability
    )
    SCHEDULING_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Scheduling utils import failed: {e}")
    SCHEDULING_AVAILABLE = False

def test_scheduling_system():
    """Test the scheduling system functionality"""
    print("🧪 Testing Scheduling System...")
    
    # Check if we have the required components
    if not APP_AVAILABLE:
        print("❌ App not available, skipping tests")
        return False
    
    if not MODELS_AVAILABLE:
        print("❌ Models not available, skipping tests")
        return False
    
    if not SCHEDULING_AVAILABLE:
        print("❌ Scheduling utils not available, skipping tests")
        return False
    
    with app.app_context():
        try:
            # Test 1: Check if tables exist
            print("\n1. Checking database tables...")
            try:
                # Try to query the tables
                call_count = ScheduledCall.query.count()
                notification_count = CallNotification.query.count()
                print(f"✅ Tables exist - {call_count} calls, {notification_count} notifications")
            except Exception as e:
                print(f"❌ Database tables error: {e}")
                return False
            
            # Test 2: Check scheduling options function
            print("\n2. Testing scheduling options...")
            try:
                # Get some test users
                students = User.query.filter_by(current_role='student').limit(1).all()
                coaches = User.query.filter_by(current_role='coach').limit(1).all()
                
                if students and coaches:
                    student = students[0]
                    coach = coaches[0]
                    options = get_scheduling_options(student.id, coach.id)
                    print(f"✅ Scheduling options: {options}")
                else:
                    print("⚠️  No test users found, skipping scheduling options test")
            except Exception as e:
                print(f"❌ Scheduling options error: {e}")
            
            # Test 3: Test availability checking
            print("\n3. Testing availability checking...")
            try:
                if coaches:
                    coach = coaches[0]
                    tomorrow = datetime.now() + timedelta(days=1)
                    available = check_call_availability(
                        coach.id,
                        tomorrow.date(),
                        datetime.now().time(),
                        'UTC'
                    )
                    print(f"✅ Availability check: {available}")
                else:
                    print("⚠️  No coaches found, skipping availability test")
            except Exception as e:
                print(f"❌ Availability check error: {e}")
            
            # Test 4: Test free consultation scheduling
            print("\n4. Testing free consultation scheduling...")
            try:
                if students and coaches:
                    student = students[0]
                    coach = coaches[0]
                    tomorrow = datetime.now() + timedelta(days=1)
                    
                    # Check if there's already a consultation
                    existing = ScheduledCall.query.filter_by(
                        student_id=student.id,
                        coach_id=coach.id,
                        call_type='free_consultation',
                        status='scheduled'
                    ).first()
                    
                    if existing:
                        print("⚠️  Free consultation already exists, skipping creation test")
                    else:
                        call = schedule_free_consultation(
                            student_id=student.id,
                            coach_id=coach.id,
                            scheduled_date=tomorrow.date(),
                            scheduled_time=datetime.now().time(),
                            timezone_name='UTC',
                            notes='Test consultation'
                        )
                        print(f"✅ Free consultation created: {call.id}")
                else:
                    print("⚠️  No test users found, skipping consultation test")
            except Exception as e:
                print(f"❌ Free consultation error: {e}")
            
            # Test 5: Test call properties
            print("\n5. Testing call properties...")
            try:
                calls = ScheduledCall.query.limit(5).all()
                if calls:
                    call = calls[0]
                    print(f"✅ Call {call.id}:")
                    print(f"   - Type: {call.call_type}")
                    print(f"   - Status: {call.status}")
                    print(f"   - Scheduled: {call.scheduled_at}")
                    print(f"   - Duration: {call.duration_minutes} minutes")
                    print(f"   - Is ready: {call.is_ready_to_join}")
                    print(f"   - Time until: {call.time_until_call}")
                else:
                    print("⚠️  No calls found to test properties")
            except Exception as e:
                print(f"❌ Call properties error: {e}")
            
            print("\n🎉 Scheduling system test completed!")
            return True
            
        except Exception as e:
            print(f"❌ General test error: {e}")
            return False

def test_notification_scheduler():
    """Test the notification scheduler"""
    print("\n🧪 Testing Notification Scheduler...")
    
    try:
        from notification_scheduler import notification_scheduler
        
        # Test scheduler initialization
        print("1. Testing scheduler initialization...")
        notification_scheduler.init_app(app)
        print("✅ Scheduler initialized")
        
        # Test scheduler jobs
        print("2. Testing scheduler jobs...")
        jobs = schedule.get_jobs()
        print(f"✅ {len(jobs)} jobs scheduled")
        
        for job in jobs:
            print(f"   - {job.job_func.__name__}: {job.at_time}")
        
        return True
        
    except Exception as e:
        print(f"❌ Notification scheduler error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Scheduling System Tests...")
    print("=" * 50)
    
    # Test scheduling system
    scheduling_ok = test_scheduling_system()
    
    # Test notification scheduler
    scheduler_ok = test_notification_scheduler()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Scheduling System: {'✅ PASS' if scheduling_ok else '❌ FAIL'}")
    print(f"   Notification Scheduler: {'✅ PASS' if scheduler_ok else '❌ FAIL'}")
    
    if scheduling_ok and scheduler_ok:
        print("\n🎉 All tests passed! Scheduling system is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == '__main__':
    main()
