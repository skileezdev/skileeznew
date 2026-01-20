# Render Deployment Configuration

## Environment Variables to Set in Render

Set these environment variables in your Render dashboard:

### Required Variables:
```
ENABLE_EMAIL_VERIFICATION=false
DATABASE_URL=your_postgresql_database_url
SESSION_SECRET=your_secret_key_here
```

### Optional Variables (only if you want email verification):
```
ENABLE_EMAIL_VERIFICATION=true
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com
```

## Key Changes Made:

1. **Email verification disabled by default** - Prevents timeout issues
2. **Conditional email configuration** - Only configures mail if email verification is enabled
3. **Timeout settings** - Added email timeout settings to prevent worker timeouts
4. **Robust error handling** - Email functions now handle missing mail configuration gracefully

## How to Deploy:

1. **Set environment variables** in Render dashboard:
   - `ENABLE_EMAIL_VERIFICATION=false` (this is the key fix!)
   - `DATABASE_URL=your_postgresql_url`
   - `SESSION_SECRET=your_secret_key`

2. **Deploy the updated code** - The signup should now work without timeouts

3. **If you want email verification later**:
   - Set `ENABLE_EMAIL_VERIFICATION=true`
   - Configure the mail environment variables
   - Redeploy

## Why This Fixes the Issue:

The original error was caused by:
- Email verification being enabled (`ENABLE_EMAIL_VERIFICATION=true`)
- But no proper SMTP configuration on Render
- This caused the email sending to hang/timeout
- Which caused the worker to be killed
- Which caused database connection issues

By setting `ENABLE_EMAIL_VERIFICATION=false`, the signup process will:
- Skip email verification entirely
- Complete quickly without timeouts
- Allow users to signup successfully
- Redirect them to login immediately
