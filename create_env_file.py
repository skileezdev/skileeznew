#!/usr/bin/env python3
"""
Script to create a .env file with test mode enabled
"""

import os

def create_env_file():
    """Create a .env file with test mode enabled"""
    
    env_content = """# Payment Test Mode Configuration
TEST_MODE=true

# Other environment variables can be added here
# STRIPE_SECRET_KEY=your_stripe_secret_key
# STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
# STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file with TEST_MODE=true")
        print("📋 Next steps:")
        print("1. Restart your Flask application:")
        print("   - Stop the current app (Ctrl+C)")
        print("   - Run: python app.py")
        print()
        print("2. Verify test mode is active:")
        print("   - Go to a contract payment page")
        print("   - Should see yellow 'Test Mode Active' banner")
        print("   - Should see blue 'Process Test Payment' button")
        print()
        print("3. Test the payment flow:")
        print("   - Click 'Process Test Payment' button")
        print("   - Should simulate payment without going to Stripe")
        print("   - Should redirect to sessions list with success message")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

if __name__ == "__main__":
    create_env_file()
