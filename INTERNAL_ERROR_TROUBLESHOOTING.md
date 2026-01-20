# Internal Server Error - Signup Troubleshooting Guide

## 🚨 **Current Issue: Internal Server Error During Account Creation**

The internal server error is back. I've implemented several fixes and debug tools to identify and resolve the issue.

## 🔧 **Fixes Applied:**

### **1. Safer Email Verification Check**
- Fixed potential circular import issues in `is_email_verification_enabled()`
- Added try-catch around email verification checks
- Default to `False` if email verification check fails

### **2. Enhanced Error Handling**
- Added comprehensive try-catch blocks
- Added detailed debug logging
- Added fallback mechanisms for all critical functions

### **3. Debug Tools Added**
- **`/debug/minimal-signup-test`** - Bypasses all complex logic
- **`/debug/signup-test`** - Tests all imports and basic functionality
- **`/debug/email-test`** - Tests email configuration

## 🧪 **Step-by-Step Troubleshooting:**

### **Step 1: Test Basic Functionality**
Visit `/debug/signup-test` to verify:
- All imports work correctly
- Database connection is working
- Basic functionality is operational

### **Step 2: Test Minimal Signup**
Visit `/debug/minimal-signup-test` to test:
- Basic signup without form validation
- Direct database operations
- Email verification function

### **Step 3: Check Logs**
Look for these debug messages in your logs:
- `DEBUG: Signup form submitted`
- `DEBUG: Form validation passed`
- `DEBUG: Creating new user`
- `DEBUG: User created successfully with ID`

### **Step 4: Test Actual Signup**
Try the normal signup process and check for specific error messages.

## 🔍 **Common Causes of Internal Server Error:**

### **1. Import Issues**
- Missing dependencies
- Circular import problems
- Module not found errors

### **2. Database Issues**
- Connection problems
- Missing tables/columns
- Permission issues

### **3. Email Configuration Issues**
- SMTP server problems
- Authentication failures
- Timeout issues

### **4. Form Validation Issues**
- CSRF token problems
- Missing form fields
- Validation errors

## 📋 **Environment Variables Check:**

Make sure these are set in Render:
```
ENABLE_EMAIL_VERIFICATION=false  # Start with this disabled
DATABASE_URL=your_postgresql_database_url
SESSION_SECRET=your_secret_key_here
```

## 🛠️ **Quick Fix Options:**

### **Option 1: Disable Email Verification Temporarily**
Set in Render environment variables:
```
ENABLE_EMAIL_VERIFICATION=false
```

### **Option 2: Use Minimal Signup Test**
The `/debug/minimal-signup-test` route bypasses all complex logic and should work.

### **Option 3: Check Specific Error**
Look at the logs for the exact error message and traceback.

## 📊 **Expected Debug Output:**

When working correctly, you should see:
```
DEBUG: Signup form submitted
DEBUG: Form data: ImmutableMultiDict([...])
DEBUG: CSRF token present: True
DEBUG: Form validation passed
DEBUG: Creating new user: user@example.com
DEBUG: Email verification enabled: False
DEBUG: User created successfully with ID: 123
```

## 🎯 **Next Steps:**

1. **Deploy the updated code** with enhanced error handling
2. **Test `/debug/minimal-signup-test`** first
3. **Check the logs** for specific error messages
4. **Try normal signup** and monitor debug output
5. **Report the specific error** if it persists

The enhanced error handling should now provide clear information about what's causing the internal server error!
