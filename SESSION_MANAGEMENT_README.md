# Session Management System Documentation

## Overview

The Session Management System is a comprehensive solution for managing learning sessions between students and coaches in the Skileez platform. It provides full lifecycle management from scheduling to completion, including rescheduling, cancellation, and progress tracking.

## 🏗️ Architecture

### Core Components

1. **Session Model** - Database model with enhanced methods
2. **Session Routes** - RESTful API endpoints for session operations
3. **Session Templates** - User interface for session management
4. **Session Forms** - Form validation and data handling
5. **Session Utilities** - Helper functions and business logic

### Database Schema

```sql
-- Session table with all management fields
CREATE TABLE session (
    id INTEGER PRIMARY KEY,
    proposal_id INTEGER NOT NULL REFERENCES proposal(id),
    session_number INTEGER NOT NULL,
    scheduled_date DATETIME,
    completed_date DATETIME,
    status VARCHAR(20) DEFAULT 'scheduled',
    student_notes TEXT,
    coach_notes TEXT,
    scheduled_at DATETIME,
    duration_minutes INTEGER,
    timezone VARCHAR(50) DEFAULT 'UTC',
    reschedule_requested BOOLEAN DEFAULT FALSE,
    reschedule_requested_by VARCHAR(20),
    reschedule_reason TEXT,
    reschedule_deadline DATETIME,
    confirmed_by_coach BOOLEAN DEFAULT FALSE
);
```

## 🔄 Session Lifecycle

### Session States

1. **Scheduled** - Session is planned and confirmed
2. **Completed** - Session finished successfully
3. **Cancelled** - Session cancelled with notice
4. **Missed** - Session missed without notice
5. **Reschedule Requested** - Pending reschedule approval

### Session Flow

```
Scheduled → [Reschedule Requested] → [Approved/Declined] → Scheduled
     ↓
Completed/Cancelled/Missed
```

## 🛠️ Implementation Details

### 1. Session Model Methods

#### Core Methods

```python
# Reschedule Management
session.is_reschedule_allowed()           # Check 10-hour rule
session.can_request_reschedule(role)      # Check user permissions
session.request_reschedule(by, reason)    # Create reschedule request
session.approve_reschedule(new_time)      # Approve with new time
session.decline_reschedule()              # Decline request

# Session Operations
session.mark_completed(notes, by)         # Mark as completed
session.mark_missed()                     # Mark as missed
session.cancel_session()                  # Cancel session

# Status and Information
session.get_status_display()              # Human-readable status
session.get_time_until_session()          # Time remaining
session.is_overdue()                      # Check if past due
session.can_be_completed()                # Check completion eligibility
```

#### Enhanced Validation

- **Reschedule Rules**: 24-hour notice for students, 48-hour for coaches
- **Time Validation**: New times must be at least 1 hour in the future
- **Reason Validation**: Reschedule reasons must be 10-500 characters
- **Status Validation**: Only scheduled sessions can be modified
- **Permission Validation**: Users can only modify their own sessions

### 2. Session Routes

#### Core Routes

```python
# Session Management
POST   /sessions/<id>/confirm              # Confirm session (coach)
GET    /sessions/<id>/reschedule           # Request reschedule form
POST   /sessions/<id>/reschedule           # Submit reschedule request
GET    /sessions/<id>/reschedule-approval  # Reschedule approval form
POST   /sessions/<id>/approve-reschedule   # Approve reschedule
POST   /sessions/<id>/decline-reschedule   # Decline reschedule
GET    /sessions/<id>/complete-form        # Session completion form
POST   /sessions/<id>/complete             # Mark session complete
POST   /sessions/<id>/cancel               # Cancel session
POST   /sessions/<id>/missed               # Mark session missed
```

#### Route Features

- **Access Control**: Only contract participants can access sessions
- **Status Validation**: Routes check session status before operations
- **Role-based Permissions**: Different actions for students vs coaches
- **Error Handling**: Comprehensive error messages and validation
- **CSRF Protection**: All forms protected against CSRF attacks

### 3. Session Templates

#### Template Structure

```
templates/sessions/
├── request_reschedule.html      # Reschedule request form
├── reschedule_approval.html     # Reschedule approval interface
└── session_completion.html      # Session completion form
```

#### Template Features

- **Responsive Design**: Mobile-friendly interface
- **Real-time Validation**: Client-side form validation
- **Status Indicators**: Clear visual status representation
- **Progress Tracking**: Contract progress visualization
- **User Feedback**: Success/error message handling

### 4. Session Forms

#### Form Classes

```python
class SessionScheduleForm(FlaskForm):
    scheduled_at = StringField('Scheduled Date/Time')
    duration_minutes = IntegerField('Duration (minutes)')
    timezone = SelectField('Timezone')

class RescheduleRequestForm(FlaskForm):
    reason = TextAreaField('Reason for Reschedule')

class RescheduleApprovalForm(FlaskForm):
    new_scheduled_at = StringField('New Date/Time')

class SessionCompletionForm(FlaskForm):
    notes = TextAreaField('Session Notes')

class SessionCancelForm(FlaskForm):
    reason = TextAreaField('Cancellation Reason')

class SessionMissedForm(FlaskForm):
    reason = TextAreaField('Reason for No-Show')
```

#### Form Validation

- **Required Fields**: Essential fields marked as required
- **Length Limits**: Reasonable character limits for text fields
- **Date Validation**: Future dates only for scheduling
- **Duration Validation**: Reasonable session duration limits
- **Timezone Support**: Multiple timezone options

## 📋 Business Rules

### Reschedule Rules

1. **Notice Requirements**:
   - Students: 24-hour notice required
   - Coaches: 48-hour notice required
   - Within 10 hours: Only students can request

2. **Response Time**:
   - 24 hours to respond to reschedule request
   - Automatic approval if no response

3. **Validation**:
   - New time must be at least 1 hour in the future
   - Reason must be 10-500 characters
   - Only one pending request per session

### Completion Rules

1. **Eligibility**:
   - Only scheduled sessions can be completed
   - Session must be in the past
   - Either student or coach can complete

2. **Notes**:
   - Optional notes up to 1000 characters
   - Notes stored based on who completed (coach/student)
   - Notes help track progress and learning outcomes

### Cancellation Rules

1. **Timing**:
   - Can cancel any scheduled session
   - Immediate cancellation (no approval needed)
   - Cancelled sessions don't count toward completion

2. **Impact**:
   - No refund for cancelled sessions
   - Session slot becomes available for rescheduling
   - Contract progress unaffected

### No-Show Rules

1. **Definition**:
   - Session past scheduled time but not completed
   - No communication from either party
   - Automatic marking after 30 minutes

2. **Consequences**:
   - Session marked as missed
   - May affect coach ratings
   - No payment for missed sessions

## 🔐 Security Features

### Access Control

- **Contract Verification**: Only contract participants can access sessions
- **Role-based Permissions**: Different actions for different roles
- **Session Ownership**: Users can only modify their own sessions
- **Status Validation**: Operations only allowed on appropriate session states

### Data Validation

- **Input Sanitization**: All user inputs validated and sanitized
- **CSRF Protection**: All forms protected against cross-site request forgery
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy
- **XSS Prevention**: Template escaping and input validation

### Audit Trail

- **Session History**: All session state changes tracked
- **User Actions**: Who performed what action when
- **Reason Tracking**: Reasons for reschedules and cancellations
- **Timestamp Logging**: All actions timestamped

## 📊 Progress Tracking

### Contract Progress

```python
# Progress calculation
progress_percentage = (completed_sessions / total_sessions) * 100
remaining_sessions = total_sessions - completed_sessions
```

### Session Statistics

- **Completed Sessions**: Successfully finished sessions
- **Scheduled Sessions**: Upcoming sessions
- **Cancelled Sessions**: Cancelled sessions
- **Missed Sessions**: No-show sessions
- **Reschedule Requests**: Pending reschedule approvals

### Performance Metrics

- **Completion Rate**: Percentage of scheduled sessions completed
- **Reschedule Rate**: Percentage of sessions rescheduled
- **No-show Rate**: Percentage of sessions missed
- **Average Session Duration**: Actual vs planned duration

## 🎨 User Experience

### Student Experience

1. **Session Scheduling**:
   - Easy scheduling with calendar interface
   - Timezone support for global scheduling
   - Duration selection based on contract

2. **Session Management**:
   - Clear session status indicators
   - Easy reschedule request process
   - Simple completion workflow

3. **Progress Tracking**:
   - Visual progress indicators
   - Session history and notes
   - Contract completion status

### Coach Experience

1. **Session Confirmation**:
   - One-click session confirmation
   - Calendar integration ready
   - Availability management

2. **Session Conduct**:
   - Session completion with notes
   - Progress tracking and feedback
   - Professional session management

3. **Business Management**:
   - Session scheduling and rescheduling
   - No-show handling and policies
   - Contract progress monitoring

## 🚀 Deployment

### Database Migration

```bash
# Run migrations to add session management fields
python deploy_migrate_simple.py
```

### Environment Variables

```bash
# Session management configuration
SESSION_RESCHEDULE_NOTICE_HOURS=24  # Student notice requirement
COACH_RESCHEDULE_NOTICE_HOURS=48    # Coach notice requirement
SESSION_RESCHEDULE_DEADLINE_HOURS=24 # Response deadline
SESSION_MIN_NOTICE_HOURS=10         # Minimum notice for reschedule
```

### Testing

```bash
# Run comprehensive session management tests
python test_session_management.py
```

## 🔮 Future Enhancements

### Planned Features

1. **Calendar Integration**:
   - Google Calendar sync
   - Outlook Calendar integration
   - Calendar conflict detection

2. **Video Integration**:
   - Video functionality has been removed from this application
   - Session recording
   - Screen sharing

3. **Automation**:
   - Automatic session reminders
   - No-show detection
   - Contract completion notifications

4. **Analytics**:
   - Session performance metrics
   - Learning progress tracking
   - Coach effectiveness analysis

### Advanced Features

1. **Recurring Sessions**:
   - Weekly/bi-weekly sessions
   - Automatic scheduling
   - Pattern-based rescheduling

2. **Session Templates**:
   - Predefined session structures
   - Learning outcome tracking
   - Assessment integration

3. **Payment Integration**:
   - Per-session payments
   - Automatic billing
   - Refund processing

## 📞 Support

### Common Issues

1. **Reschedule Not Working**:
   - Check notice requirements
   - Verify session status
   - Ensure proper permissions

2. **Completion Issues**:
   - Verify session is in the past
   - Check session status
   - Ensure contract is active

3. **Access Denied**:
   - Verify contract participation
   - Check user role
   - Ensure session ownership

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check session state
session = Session.query.get(session_id)
print(f"Status: {session.status}")
print(f"Reschedule requested: {session.reschedule_requested}")
print(f"Can be completed: {session.can_be_completed()}")
```

The Session Management System provides a robust, secure, and user-friendly solution for managing learning sessions in the Skileez platform. It handles all edge cases, provides comprehensive validation, and offers a smooth user experience for both students and coaches.
