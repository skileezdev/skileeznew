# Email Verification Setup for Render Deployment

## 🎯 **Goal: Enable Email Verification on Render**

You want email verification to be active. Here's how to configure it properly on Render to avoid timeout issues.

## 🔧 **Environment Variables to Set in Render Dashboard**

### **Required Variables:**
```
ENABLE_EMAIL_VERIFICATION=true
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=skileezverf@gmail.com
MAIL_PASSWORD=wghd tnjr kbda mjie
MAIL_DEFAULT_SENDER=skileezverf@gmail.com
```

### **Optional Variables:**
```
BASE_URL=https://your-app-name.onrender.com
DATABASE_URL=your_postgresql_database_url
SESSION_SECRET=your_secret_key_here
```

## 🛠️ **Key Improvements Made:**

### **1. Robust Timeout Handling**
- Increased email timeout to 15 seconds
- Added connection timeout of 10 seconds
- Added signal-based timeout handling for email operations

### **2. Better Error Recovery**
- Email failures won't crash the signup process
- Detailed logging for debugging
- Graceful fallback if email service is unavailable

### **3. Render-Optimized Configuration**
- Proper SMTP settings for Gmail
- Timeout settings that work with Render's infrastructure
- Error handling that prevents worker timeouts

## 📋 **Step-by-Step Setup:**

### **Step 1: Set Environment Variables in Render**
1. Go to your Render dashboard
2. Navigate to your service
3. Go to "Environment" tab
4. Add these variables:

```
ENABLE_EMAIL_VERIFICATION=true
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=skileezverf@gmail.com
MAIL_PASSWORD=wghd tnjr kbda mjie
MAIL_DEFAULT_SENDER=skileezverf@gmail.com
BASE_URL=https://your-app-name.onrender.com
```

### **Step 2: Deploy the Updated Code**
The code has been updated with:
- Better timeout handling
- Robust error recovery
- Render-optimized email configuration

### **Step 3: Test Email Verification**
1. Try signing up as a student or coach
2. Check if verification email is sent
3. Check Render logs for any email-related errors

## 🔍 **Troubleshooting:**

### **If emails still timeout:**
1. Check Render logs for email errors
2. Verify Gmail app password is correct
3. Ensure BASE_URL is set correctly
4. Check if Gmail account has 2FA enabled

### **If emails don't send:**
1. Verify MAIL_USERNAME and MAIL_PASSWORD
2. Check if Gmail app password is valid
3. Ensure MAIL_SERVER and MAIL_PORT are correct

### **If signup still fails:**
1. Check Render logs for specific errors
2. Verify all environment variables are set
3. Test with a simple email address

## 📧 **Gmail Setup (if needed):**

If you need to create a new Gmail app password:
1. Enable 2-Factor Authentication on Gmail
2. Go to Google Account settings
3. Security → App passwords
4. Generate password for "Mail"
5. Use that password in MAIL_PASSWORD

## ✅ **Expected Behavior:**

With email verification enabled:
1. User fills out signup form
2. User account is created
3. Verification email is sent (with timeout protection)
4. User receives email with verification link
5. User clicks link to verify account
6. User can then login

## 🚨 **Fallback Behavior:**

If email sending fails:
1. User account is still created
2. User gets a message about email issues
3. User can still login (account is auto-verified)
4. No worker timeouts or crashes

This ensures your signup process is robust and won't break even if email service has issues!
