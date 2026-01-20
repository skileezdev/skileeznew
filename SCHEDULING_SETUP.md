# Skileez Scheduling System Setup Guide

## Overview

The Skileez scheduling system handles:
- Session scheduling and management
- Email notifications and reminders
- Video session coordination
- Automatic cleanup of old data

## Components

### 1. Notification Scheduler
- **File**: `notification_scheduler.py`
- **Purpose**: Background scheduler for notifications and reminders
- **Features**:
  - 24-hour session reminders
  - 1-hour session reminders
  - 15-minute session reminders
  - Call ready notifications
  - Overdue call marking
  - Cleanup of old notifications

### 2. Scheduler Webhook
- **Endpoint**: `/api/scheduler`
- **Purpose**: External trigger for scheduled tasks
- **Method**: POST
- **Body**: `{"task": "all"}` or specific task

### 3. Email Notifications
- **File**: `email_utils.py`
- **Features**:
  - Session scheduled notifications
  - Session reminders (24h, 1h, 15min)
  - Join session links included

## Setup Instructions

### Step 1: Deploy Your App
Make sure your app is deployed on Render and accessible.

### Step 2: Test the Scheduler Webhook
Run the test script to verify the webhook is working:

```bash
python test_scheduler_webhook.py https://your-app.onrender.com
```

### Step 3: Set Up Cron Job
Use [cron-job.org](https://cron-job.org) to set up automatic scheduling:

1. **Sign up** for a free account at cron-job.org
2. **Create a new cron job**:
   - **Title**: Skileez Scheduler
   - **URL**: `https://your-app.onrender.com/api/scheduler`
   - **Method**: POST
   - **Headers**: `Content-Type: application/json`
   - **Body**: `{"task": "all"}`
   - **Schedule**: Every 5 minutes
   - **Retry on failure**: Yes (3 retries)

### Step 4: Verify Setup
1. **Check Render logs** for scheduler activity
2. **Test with a scheduled session**:
   - Create a session for 1 hour from now
   - Wait for the 1-hour reminder email
   - Check that notifications are sent

## Troubleshooting

### Scheduler Not Running
- Check if the notification scheduler is initialized in `app.py`
- Verify the webhook endpoint is accessible
- Check Render logs for errors

### No Email Notifications
- Verify email configuration in `app.py`
- Check Gmail app password is correct
- Test email sending manually

### Can't Join Sessions
- Check session timing validation in `video_utils.py`
- Verify session status is 'scheduled'
- Check if within allowed time window (2 hours before/after)

### Webhook Not Responding
- Verify the endpoint URL is correct
- Check if the app is running on Render
- Test with the provided test script

## Monitoring

### Render Logs
Monitor your Render logs for:
- Scheduler initialization messages
- Email sending confirmations
- Error messages

### Test Scripts
Use the provided test scripts:
- `test_scheduler_webhook.py` - Test webhook functionality
- `monitor_scheduler.py` - Comprehensive status check

## Configuration

### Email Settings
Configure in `app.py`:
```python
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
```

### Time Windows
Adjust in `video_utils.py`:
- Session join window: 2 hours before/after scheduled time
- Video session window: 4 hours after start
- Early join window: 30 minutes before scheduled time

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Render logs for error messages
3. Test individual components with the provided scripts
4. Verify all configuration settings are correct

## Security Notes

- The webhook endpoint is protected by CSRF exemption
- Email credentials should be stored as environment variables
- Session validation ensures only authorized users can join
- All database operations are wrapped in try-catch blocks
