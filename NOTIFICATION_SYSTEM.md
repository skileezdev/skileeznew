# Notification System Documentation

## Quick Setup Guide

### 1. Database Setup
```bash
# Run migrations to create notification table
flask db upgrade
```

### 2. Test the System
```bash
# Run the test script to verify functionality
python test_notifications.py
```

### 3. Verify Integration
- Check that notification bell appears in navigation
- Send a message to test real-time notifications
- Create a contract to test contract notifications

## Overview

The Skileez notification system provides real-time updates to users about important events in the platform. It includes a modern UI with dropdown notifications, real-time polling, toast notifications, and comprehensive backend support.

## Features

### ✅ Implemented Features

1. **Real-time Notification Display**
   - Notification bell with unread count badge
   - Dropdown notification list
   - Real-time polling (every 30 seconds)
   - Toast notifications for new events

2. **Notification Types**
   - Contract notifications (sent, accepted, rejected, payment received)
   - Session notifications (scheduled, rescheduled, cancelled, completed)
   - Message notifications (new messages)
   - Job notifications (proposals, acceptances)
   - System notifications (profile updates, role switches)
   - Payment notifications (success, failure, refunds)

3. **Notification Management**
   - Mark individual notifications as read
   - Mark all notifications as read
   - View all notifications page
   - Automatic cleanup of old notifications

4. **Modern UI/UX**
   - Animated notification badges
   - Smooth dropdown animations
   - Responsive design
   - Icon-based notification types
   - Time-ago display

## Technical Implementation

### Backend Components

#### 1. Notification Model (`models.py`)

```python
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_id = db.Column(db.Integer)
    related_type = db.Column(db.String(50))
    
    # Methods
    def to_dict(self)
    @classmethod
    def create_notification(cls, user_id, title, message, notification_type, related_id=None, related_type=None)
    @classmethod
    def get_unread_count(cls, user_id)
    @classmethod
    def get_recent_notifications(cls, user_id, limit=10)
    @classmethod
    def mark_as_read(cls, notification_id, user_id)
    @classmethod
    def mark_all_as_read(cls, user_id)
```

#### 2. Notification Utilities (`notification_utils.py`)

Comprehensive utility functions for creating different types of notifications:

- `create_contract_notification(contract, notification_type, recipient_id=None)`
- `create_session_notification(session, notification_type)`
- `create_message_notification(sender, recipient, message_preview)`
- `create_system_notification(user_id, title, message, notification_type='system')`
- `create_job_notification(job, notification_type)`
- `create_profile_notification(user, notification_type)`
- `create_payment_notification(user, amount, status, contract_title=None)`
- `create_bulk_notification(user_ids, title, message, notification_type='system')`
- `cleanup_old_notifications(days_old=30)`

#### 3. API Endpoints (`routes.py`)

```python
@app.route('/api/notifications')
@app.route('/api/notifications/unread-count')
@app.route('/api/notifications/<int:notification_id>/mark-read', methods=['POST'])
@app.route('/api/notifications/mark-all-read', methods=['POST'])
@app.route('/notifications')
```

### Frontend Components

#### 1. Notification Manager (`static/js/notifications.js`)

Modern JavaScript class that handles:
- Real-time notification polling
- Toast notification system
- Dropdown management
- Mark as read functionality
- Animation and UI updates

#### 2. Notification UI (`templates/base.html`)

- Notification bell with badge
- Dropdown notification list
- Responsive design
- Integration with existing UI

#### 3. Notification Styles (`static/css/notifications.css`)

- Modern animations
- Responsive design
- Icon styling
- Hover effects

## Usage Examples

### Creating Notifications

#### 1. Contract Notifications

```python
from notification_utils import create_contract_notification

# When a contract is sent
create_contract_notification(contract, 'contract_sent')

# When a contract is accepted
create_contract_notification(contract, 'contract_accepted')

# When payment is received
create_contract_notification(contract, 'payment_received')
```

#### 2. Message Notifications

```python
from notification_utils import create_message_notification

# When a message is sent
create_message_notification(sender, recipient, message_content)
```

#### 3. System Notifications

```python
from notification_utils import create_system_notification

# Profile update
create_system_notification(user.id, "Profile Updated", "Your profile has been updated successfully")

# Role switch
create_system_notification(user.id, "Role Switched", f"You are now in {user.current_role} mode")
```

#### 4. Payment Notifications

```python
from notification_utils import create_payment_notification

# Successful payment
create_payment_notification(user, 99.99, 'success', 'Contract Title')

# Failed payment
create_payment_notification(user, 99.99, 'failed', 'Contract Title')
```

### Frontend Integration

#### 1. Manual Notification Check

```javascript
// Check for new notifications
if (window.notificationManager) {
    window.notificationManager.checkNotifications();
}
```

#### 2. Show Toast Notification

```javascript
// Show a toast notification
if (window.notificationManager) {
    window.notificationManager.showToast('Payment successful!', 'success');
}
```

## Testing

Run the test script to verify the notification system:

```bash
python test_notifications.py
```

This will test:
- Notification creation
- Model methods
- Mark as read functionality
- Different notification types
- System integration

## Configuration

### Polling Interval

The notification system polls for updates every 30 seconds by default. This can be adjusted in `static/js/notifications.js`:

```javascript
startPolling() {
    this.pollingInterval = setInterval(() => {
        this.updateUnreadCount();
    }, 30000); // 30 seconds
}
```

### Cleanup Schedule

Old notifications are automatically cleaned up. Configure the cleanup period in `notification_utils.py`:

```python
def cleanup_old_notifications(days_old=30):
    # Clean up notifications older than 30 days
```

## Integration Points

### 1. Contract System

Notifications are automatically created for:
- Contract proposals sent
- Contract acceptance/rejection
- Payment received
- Contract cancellation
- Contract expiration

### 2. Messaging System

Notifications are created when:
- New messages are sent
- Messages are received

### 3. Session Management

Notifications for:
- Session scheduling
- Session rescheduling
- Session cancellation
- Session completion
- Session reminders

### 4. Payment System

Notifications for:
- Successful payments
- Failed payments
- Refunds
- Payment processing

### 5. Profile Management

Notifications for:
- Profile updates
- Role switches
- Account verification

## Best Practices

### 1. Error Handling

Always wrap notification creation in try-catch blocks:

```python
try:
    create_contract_notification(contract, 'contract_sent')
except Exception as e:
    logger.error(f"Error creating notification: {e}")
```

### 2. Performance

- Use bulk notifications for multiple users
- Clean up old notifications regularly
- Limit notification polling frequency

### 3. User Experience

- Keep notification messages concise
- Use appropriate notification types
- Provide actionable information
- Don't spam users with too many notifications

## Troubleshooting

### Common Issues

1. **Notifications not appearing**
   - Check if the notification bell exists in the DOM
   - Verify JavaScript is loading properly
   - Check browser console for errors

2. **Real-time updates not working**
   - Verify polling is enabled
   - Check network connectivity
   - Ensure API endpoints are accessible

3. **Notification creation failing**
   - Check database connection
   - Verify user exists
   - Check notification utility imports

### Debug Mode

Enable debug logging in `notification_utils.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Push Notifications**
   - Browser push notifications
   - Mobile app notifications
   - Email notifications

2. **Advanced Filtering**
   - Filter by notification type
   - Date range filtering
   - Search functionality

3. **Notification Preferences**
   - User-configurable notification settings
   - Notification frequency controls
   - Type-specific preferences

4. **Real-time WebSocket**
   - Replace polling with WebSocket connections
   - Instant notification delivery
   - Better performance

## Support

For issues with the notification system:

1. Check the browser console for JavaScript errors
2. Verify the notification database table exists
3. Run the test script to verify functionality
4. Check the application logs for backend errors

The notification system is designed to be robust and user-friendly, providing essential real-time updates while maintaining good performance and user experience.
