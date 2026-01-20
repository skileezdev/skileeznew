#!/usr/bin/env python3
"""
Script to help set up test mode for Render deployment
"""

import os

def render_test_mode_instructions():
    """Provide instructions for setting up test mode on Render"""
    
    print("🚀 Render Test Mode Setup")
    print("=" * 40)
    
    print("Since you're deploying on Render, you need to set the environment variable in your Render dashboard.")
    print()
    print("📋 Step-by-Step Instructions:")
    print()
    print("1. 🌐 Go to Render Dashboard:")
    print("   - Log into your Render account")
    print("   - Navigate to your Flask service")
    print()
    print("2. ⚙️ Add Environment Variable:")
    print("   - Go to the 'Environment' tab")
    print("   - Click 'Add Environment Variable'")
    print("   - Key: TEST_MODE")
    print("   - Value: true")
    print("   - Click 'Save Changes'")
    print()
    print("3. 🔄 Redeploy Your App:")
    print("   - Go to 'Manual Deploy' tab")
    print("   - Click 'Deploy latest commit'")
    print("   - Wait for deployment to complete")
    print()
    print("4. ✅ Verify Test Mode:")
    print("   - Once deployed, navigate to a contract payment page")
    print("   - You should see yellow 'Test Mode Active' banner")
    print("   - You should see blue 'Process Test Payment' button")
    print()
    print("🔧 Alternative: Update render.yaml")
    print("You can also add this to your render.yaml file:")
    print()
    print("services:")
    print("  - type: web")
    print("    name: your-app-name")
    print("    envVars:")
    print("      - key: TEST_MODE")
    print("        value: true")
    print()
    print("📝 Note: After setting the environment variable, your app will automatically redeploy.")
    print("   The test mode will be active in your production environment.")

def check_render_yaml():
    """Check if render.yaml exists and suggest updates"""
    
    print("\n📄 Render.yaml Check")
    print("=" * 25)
    
    if os.path.exists('render.yaml'):
        print("✅ render.yaml file exists")
        print("You can add TEST_MODE to your render.yaml file:")
        print()
        print("Add this under your service configuration:")
        print("  envVars:")
        print("    - key: TEST_MODE")
        print("      value: true")
    else:
        print("❌ render.yaml file not found")
        print("You'll need to set the environment variable manually in the Render dashboard.")

if __name__ == "__main__":
    render_test_mode_instructions()
    check_render_yaml()
