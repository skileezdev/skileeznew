# Enterprise Scheduling System

A comprehensive, enterprise-grade scheduling system built for Skileez. This system provides robust scheduling capabilities comparable to Cal.com with advanced features for coaching platforms.

## 🚀 Features

### Core Scheduling Engine
- **Real-time Availability Checking**: Dynamic availability calculation based on coach schedules
- **Double-booking Prevention**: Database-level conflict detection and prevention
- **Timezone Handling**: Full timezone support with automatic conversion
- **Buffer Time Management**: Configurable buffer times between sessions
- **Working Hours Management**: Per-day working hours configuration

### Pre/Post Contract Scheduling
- **Free Consultations**: 15-minute free consultation booking system
- **Paid Sessions**: Full session scheduling with payment verification
- **Contract Status Checking**: Automatic validation of contract status before scheduling
- **Session Type Management**: Different flows for consultation vs paid sessions

### Video Integration Removed
- **Video functionality has been completely removed from this application**
- **LiveKit integration is no longer available**
- **All video-related features have been eliminated**

### Advanced Features
- **Rescheduling Workflow**: Approval-based rescheduling system
- **Cancellation Policies**: Configurable cancellation rules and policies
- **Email/SMS Notifications**: Automated notifications for all scheduling events
- **Calendar Integration**: Google Calendar and Outlook sync capabilities
- **Buffer Times**: Configurable buffer times between sessions
- **Exception Management**: Block specific dates/times for coaches

### User Interface
- **Professional Calendar View**: Clean, intuitive scheduling interface
- **Real-time Updates**: Live availability updates without page refresh
- **Mobile Responsive**: Fully responsive design for all devices
- **Accessibility**: WCAG compliant interface

## 📋 System Architecture

### Database Models

#### CoachAvailability
Manages coach working hours and availability settings:
```python
class CoachAvailability(db.Model):
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_available = db.Column(db.Boolean, default=True)
    timezone = db.Column(db.String(50), default='UTC')
    # Working hours for each day (stored as minutes from midnight)
    monday_start = db.Column(db.Integer, default=540)  # 9:00 AM
    monday_end = db.Column(db.Integer, default=1020)   # 5:00 PM
    # ... similar for other days
    session_duration = db.Column(db.Integer, default=60)
    buffer_before = db.Column(db.Integer, default=0)
    buffer_after = db.Column(db.Integer, default=15)
    consultation_available = db.Column(db.Boolean, default=True)
    consultation_duration = db.Column(db.Integer, default=15)
```

#### ScheduledSession
Enhanced session management with availability checking:
```python
class ScheduledSession(db.Model):
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    session_type = db.Column(db.String(50), default='paid')
    is_consultation = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default='scheduled')
    # Video functionality removed
    # livekit_room_name and livekit_room_sid columns removed
    # Rescheduling
    reschedule_requested = db.Column(db.Boolean, default=False)
    reschedule_requested_by = db.Column(db.String(20))
    reschedule_reason = db.Column(db.Text)
```

#### BookingRule
Scheduling policies and rules:
```python
class BookingRule(db.Model):
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cancellation_hours = db.Column(db.Integer, default=24)
    reschedule_hours = db.Column(db.Integer, default=12)
    no_show_policy = db.Column(db.String(50), default='charge_full')
    require_payment_before = db.Column(db.Boolean, default=True)
    send_reminder_hours = db.Column(db.Integer, default=24)
```

### API Endpoints

#### Availability Management
- `GET /api/scheduling/availability/<coach_id>` - Get coach availability
- `POST /api/scheduling/book` - Book a new session
- `GET /scheduling/availability/<coach_id>` - View coach availability page

#### Session Management
- `GET /scheduling/session/<session_id>` - View session details
- `POST /scheduling/session/<session_id>/cancel` - Cancel session
- `POST /scheduling/session/<session_id>/reschedule` - Request reschedule
- `POST /scheduling/session/<session_id>/approve-reschedule` - Approve reschedule
- `POST /scheduling/session/<session_id>/start` - Start video session

#### Coach Settings
- `GET /scheduling/coach/settings` - Coach scheduling settings
- `POST /scheduling/coach/settings` - Update coach settings
- `GET /scheduling/coach/exceptions` - Manage availability exceptions

## 🛠️ Installation & Setup

### 1. Database Migration
Run the migration to create the scheduling tables:
```bash
flask db upgrade
```

### 2. Environment Variables
Add these to your `.env` file:
```env
# Video functionality has been removed from this application
# LiveKit configuration is no longer needed

# Timezone Support
DEFAULT_TIMEZONE=UTC

# Notification Settings
SEND_EMAIL_NOTIFICATIONS=true
SEND_SMS_NOTIFICATIONS=false
```

### 3. Dependencies
Add to `requirements.txt`:
```
pytz>=2023.3
python-dateutil>=2.8.2
```

## 📖 Usage Guide

### For Coaches

#### Setting Up Availability
1. Navigate to `/scheduling/coach/settings`
2. Configure working hours for each day
3. Set session duration and buffer times
4. Configure consultation settings
5. Set booking rules and policies

#### Managing Exceptions
1. Go to `/scheduling/coach/exceptions`
2. Add blocked dates or special hours
3. Set reasons for exceptions

#### Viewing Sessions
- Dashboard: `/scheduling/dashboard`
- Session details: `/scheduling/session/<session_id>`

### For Students

#### Booking Sessions
1. Browse coaches and select one
2. View their availability at `/scheduling/availability/<coach_id>`
3. Choose between free consultation or paid session
4. Select available time slot
5. Complete booking

#### Managing Bookings
- View upcoming sessions on dashboard
- Request reschedules if needed
- Cancel sessions within allowed timeframe

## 🔧 Configuration

### Coach Availability Settings
```python
# Example: Set up a coach's availability
availability = CoachAvailability(
    coach_id=coach.id,
    timezone='America/New_York',
    monday_start=540,  # 9:00 AM
    monday_end=1020,   # 5:00 PM
    session_duration=60,
    buffer_after=15,
    consultation_available=True,
    consultation_duration=15
)
```

### Booking Rules
```python
# Example: Configure booking policies
rules = BookingRule(
    coach_id=coach.id,
    cancellation_hours=24,
    reschedule_hours=12,
    no_show_policy='charge_full',
    require_payment_before=True,
    send_reminder_hours=24
)
```

## 🔌 Video Integration Removed

Video calling functionality has been completely removed from this application. LiveKit integration is no longer available.

## 📧 Notification System

### Email Notifications
The system sends automated emails for:
- Booking confirmations
- Session reminders (24h before)
- Reschedule requests
- Cancellation confirmations
- Session completion

### SMS Notifications (Optional)
Configure SMS notifications for:
- Session reminders
- Last-minute changes
- No-show alerts

## 🗓️ Calendar Integration

### Google Calendar
- Sync coach availability to Google Calendar
- Import external events to block time
- Export sessions to student calendars

### Outlook Calendar
- Similar integration for Outlook users
- Bidirectional sync capabilities

## 🔒 Security & Privacy

### Data Protection
- All scheduling data encrypted at rest
- Secure API endpoints with authentication
- GDPR compliant data handling

### Access Control
- Role-based access control
- Session-specific permissions
- Audit logging for all actions

## 🧪 Testing

### Unit Tests
```bash
# Run scheduling system tests
python -m pytest tests/test_scheduling.py

# Test availability calculation
python -m pytest tests/test_availability.py

# Test booking workflow
python -m pytest tests/test_booking.py
```

### Integration Tests
```bash
# Video functionality has been removed from this application

# Test notification system
python -m pytest tests/test_notifications.py
```

## 📊 Monitoring & Analytics

### Key Metrics
- Booking conversion rates
- Session completion rates
- Reschedule/cancellation rates
- Coach utilization rates

### Performance Monitoring
- API response times
- Database query performance
- Video functionality has been removed from this application

## 🚀 Deployment

### Production Checklist
- [ ] Run database migrations
- [ ] Configure environment variables
- [x] Video functionality has been removed from this application
- [ ] Configure email/SMS services
- [ ] Set up monitoring and logging
- [ ] Test all scheduling workflows
- [ ] Configure backup strategies

### Scaling Considerations
- Database indexing for performance
- Caching for availability calculations
- Load balancing for video sessions
- CDN for static assets

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

### Code Standards
- Follow PEP 8 style guide
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation

## 📝 License

This scheduling system is part of the Skileez platform and follows the same licensing terms.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

---

**Built with ❤️ for the Skileez platform**
