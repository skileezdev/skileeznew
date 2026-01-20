#!/usr/bin/env python3
"""
Test script to verify that all required packages can be imported correctly
This helps identify any remaining import issues before deployment
"""

import sys
import importlib

def test_imports():
    """Test all critical imports"""
    print("Testing package imports...")
    print("=" * 50)
    
    # Core Flask dependencies
    core_packages = [
        'flask',
        'flask_sqlalchemy', 
        'flask_migrate',
        'flask_wtf',
        'flask_mail',
        'jinja2',
        'werkzeug',
        'wtforms'
    ]
    
    # Database dependencies
    db_packages = [
        'sqlalchemy',
        'psycopg2'
    ]
    
    # Web server
    server_packages = [
        'gunicorn'
    ]
    
    # Authentication & Security
    auth_packages = [
        'jwt',
        'email_validator'
    ]
    
    # Environment & Configuration
    config_packages = [
        'dotenv'
    ]
    
    # Payment Processing
    payment_packages = [
        'stripe'
    ]
    
    # Timezone & Date Handling
    timezone_packages = [
        'pytz',
        'dateutil'
    ]
    
    # HTTP Requests
    http_packages = [
        'requests'
    ]
    
    # Scheduling System Dependencies
    scheduling_packages = [
        'schedule'
    ]
    
    # Video functionality has been removed from this application
    video_packages = []
    
    # Additional Utilities
    util_packages = [
        'click',
        'markupsafe'
    ]
    
    all_packages = (
        core_packages + db_packages + server_packages + 
        auth_packages + config_packages + payment_packages + 
        timezone_packages + http_packages + scheduling_packages + 
        video_packages + util_packages
    )
    
    failed_imports = []
    successful_imports = []
    
    for package in all_packages:
        try:
            importlib.import_module(package)
            successful_imports.append(package)
            print(f"✅ {package}")
        except ImportError as e:
            failed_imports.append(package)
            print(f"❌ {package}: {e}")
    
    print("\n" + "=" * 50)
    print(f"Successful imports: {len(successful_imports)}")
    print(f"Failed imports: {len(failed_imports)}")
    
    if failed_imports:
        print("\n❌ Failed imports:")
        for package in failed_imports:
            print(f"   - {package}")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def test_video_specific():
    """Video functionality has been removed from this application"""
    print("\nVideo functionality has been removed from this application")
    print("=" * 50)
    
    # Video functionality has been removed from this application
    
    print("✅ Video functionality has been removed from this application")
    return True

def test_sqlalchemy():
    """Test SQLAlchemy functionality"""
    print("\nTesting SQLAlchemy imports...")
    print("=" * 50)
    
    try:
        from sqlalchemy import create_engine, text, inspect
        print("✅ SQLAlchemy core imports successful")
        
        from sqlalchemy.exc import ProgrammingError
        print("✅ SQLAlchemy exceptions imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ SQLAlchemy import error: {e}")
        return False

if __name__ == "__main__":
    print("Testing package requirements for production deployment...")
    
    # Test all imports
    imports_ok = test_imports()
    
    # Test specific critical packages
    video_ok = test_video_specific()
    sqlalchemy_ok = test_sqlalchemy()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"General imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Video functionality: {'✅ REMOVED'}")
    print(f"SQLAlchemy imports: {'✅ PASS' if sqlalchemy_ok else '❌ FAIL'}")
    
    if imports_ok and video_ok and sqlalchemy_ok:
        print("\n🎉 All tests passed! Ready for deployment.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please fix the issues before deployment.")
        sys.exit(1)
