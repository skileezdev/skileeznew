#!/usr/bin/env python3
"""
Script to restart Flask app with test mode enabled
"""

import os
import subprocess
import sys
import time
from dotenv import load_dotenv

def restart_flask_with_test_mode():
    """Restart Flask app with test mode enabled"""
    
    print("🔄 Restarting Flask App with Test Mode")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Verify test mode is enabled
    test_mode = os.environ.get('TEST_MODE', 'false')
    if test_mode.lower() != 'true':
        print("❌ TEST_MODE is not enabled in .env file")
        print("Please run: python create_env_file.py")
        return False
    
    print("✅ TEST_MODE is enabled")
    print("🔄 Starting Flask application...")
    print()
    print("📋 Instructions:")
    print("1. The Flask app will start with test mode enabled")
    print("2. You should see 'TEST_MODE: True' in the startup logs")
    print("3. Navigate to a contract payment page")
    print("4. Look for the yellow 'Test Mode Active' banner")
    print("5. Use the blue 'Process Test Payment' button")
    print()
    print("🛑 To stop the app: Press Ctrl+C")
    print("=" * 40)
    
    try:
        # Start Flask app
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Flask app stopped by user")
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        return False
    
    return True

if __name__ == "__main__":
    restart_flask_with_test_mode()
