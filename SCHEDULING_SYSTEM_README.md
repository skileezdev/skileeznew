# 🗓️ Scheduling System Implementation

## Overview

The Skileez scheduling system provides a **dual scheduling approach** that automatically adapts based on the relationship between students and coaches:

1. **Free 15-minute consultations** - Available immediately when students and coaches connect
2. **Paid learning sessions** - Unlocked after contract acceptance and payment

## 🎯 Key Features

### ✅ **Dual Scheduling System**
- **Free Consultations**: 15-minute video calls for initial discussions
- **Paid Sessions**: Full learning sessions based on contract terms
- **Automatic Detection**: System automatically shows appropriate scheduling options

### ✅ **Interactive Call Cards**
- **Real-time Status**: Shows call status (scheduled, ready, active, completed)
- **Join Buttons**: Functional buttons that appear when calls are ready
- **Countdown Timers**: Real-time countdown to call start time
- **Reschedule/Cancel**: Full call management capabilities

### ✅ **Video Integration Removed**
- **Video functionality has been removed from this application**
- **Video functionality has been removed from this application**

### ✅ **Automated Notifications**
- **Email confirmations** when calls are scheduled
- **24-hour reminders** before calls
- **1-hour reminders** before calls
- **Real-time notifications** when calls are ready to join
- **In-app notifications** for all call events

### ✅ **Smart Availability Checking**
- **Conflict detection** to prevent double-booking
- **Real-time availability** checking via API
- **Timezone handling** for global users

## 🏗️ System Architecture

### Database Models

#### `ScheduledCall`
```python
- id: Primary key
- student_id: Student user ID
- coach_id: Coach user ID
- call_type: 'free_consultation' or 'paid_session'
- scheduled_at: UTC datetime
- duration_minutes: Call duration
- status: scheduled, active, completed, cancelled, missed
- livekit_room_name: Removed (video functionality no longer available)
- contract_id: Associated contract (for paid sessions)
- notes: Call notes
- started_at, ended_at: Call timing
- rescheduled_from: Previous call ID if rescheduled
```

#### `CallNotification`
```python
- id: Primary key
- call_id: Associated call ID
- notification_type: scheduled, reminder_24h, reminder_1h, ready, completed
- sent_at: When notification was sent
- sent_to_student, sent_to_coach: Boolean flags
- email_sent, notification_sent: Delivery status
```

### Key Components

#### 1. **Scheduling Utils** (`scheduling_utils.py`)
- Core scheduling logic
- Notification sending
- Video functionality removed
- Availability checking

#### 2. **Notification Scheduler** (`notification_scheduler.py`)
- Background task scheduler
- Automated reminders
- Call status management

#### 3. **Interactive Templates**
- `schedule_free_consultation.html`
- `schedule_paid_session.html`
- `call_card.html` (interactive call cards)
- `video_room.html` (Removed - video functionality no longer available)

#### 4. **JavaScript Manager** (`scheduling.js`)
- Dynamic button updates
- Real-time availability checking
- WebSocket integration
- Call management

## 🚀 Implementation Details

### Scheduling Flow

#### Free Consultation Flow
1. **Student clicks** "Schedule Free 15-min Call"
2. **System checks** if consultation already exists
3. **Student selects** date, time, timezone
4. **System validates** coach availability
5. **Call is created** and notifications sent
6. **Interactive call card** appears in chat

#### Paid Session Flow
1. **Student clicks** "Schedule Learning Session" (only after contract payment)
2. **System loads** contract details
3. **Student selects** date, time, duration, timezone
4. **System validates** coach availability
5. **Session is created** and notifications sent
6. **Interactive call card** appears in chat

### Call Lifecycle

1. **Scheduled** → Call is created and confirmed
2. **Ready** → Within 5 minutes of start time
3. **Active** → Call is in progress
4. **Completed** → Call has ended
5. **Cancelled** → Call was cancelled
6. **Missed** → No one joined within 15 minutes

### Notification System

#### Automated Notifications
- **Immediate**: When call is scheduled
- **24h before**: Reminder email and notification
- **1h before**: Final reminder
- **Ready**: When call is ready to join
- **Completed**: After call ends

#### Notification Types
- **Email notifications** with calendar integration
- **In-app notifications** with real-time updates
- **System messages** in chat
- **Interactive call cards** with join buttons

## 🎨 User Interface

### Dynamic Scheduling Buttons
```html
<!-- Free consultation button -->
<a href="/schedule/free-consultation/{{ coach.id }}" class="btn-primary">
    <i data-feather="phone"></i>
    Schedule Free 15-min Call
</a>

<!-- Paid session button -->
<a href="/schedule/paid-session/{{ contract.id }}" class="btn-primary">
    <i data-feather="calendar"></i>
    Schedule Learning Session
</a>
```

### Interactive Call Cards
```html
<!-- Call card with join button -->
<div class="call-card">
    <div class="call-info">
        <h4>Free Consultation Call</h4>
        <p>Tomorrow at 2:00 PM (15 minutes)</p>
        <span class="status-badge">Ready to Join</span>
    </div>
    <div class="call-actions">
        <a href="/calls/{{ call.id }}/join" class="btn-join">
            <i data-feather="play"></i>
            Join Call
        </a>
    </div>
</div>
```

### Video Room Interface
```html
<!-- Video functionality has been removed from this application -->
<div class="video-room">
    <div class="participant-grid">
        <!-- Video participants -->
    </div>
    <div class="call-controls">
        <button class="control-btn" onclick="toggleVideo()">
            <i data-feather="video"></i>
        </button>
        <button class="control-btn" onclick="toggleAudio()">
            <i data-feather="mic"></i>
        </button>
        <button class="control-btn danger" onclick="endCall()">
            <i data-feather="phone-off"></i>
        </button>
    </div>
</div>
```

## 🔧 Configuration

### Environment Variables
```bash
# Video functionality has been removed from this application
# LiveKit configuration is no longer needed

# Email Configuration (already configured)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=skileezverf@gmail.com
MAIL_PASSWORD=wghd tnjr kbda mjie
```

### Database Migration
```bash
# Run the migration to create scheduling tables
flask db upgrade
```

## 🧪 Testing

### Run Test Script
```bash
python test_scheduling.py
```

### Manual Testing
1. **Create test users** (student and coach)
2. **Schedule free consultation** between them
3. **Verify notifications** are sent
4. **Test call card** appears in chat
5. **Test video room** functionality
6. **Test rescheduling** and cancellation

## 📱 API Endpoints

### Scheduling Endpoints
- `GET/POST /schedule/free-consultation/<coach_id>` - Schedule free consultation
- `GET/POST /schedule/paid-session/<contract_id>` - Schedule paid session
- `GET /calls/<call_id>` - View call details
- `GET /calls/<call_id>/join` - Join call
- `POST /calls/<call_id>/end` - End call
- `POST /calls/<call_id>/cancel` - Cancel call
- `GET/POST /calls/<call_id>/reschedule` - Reschedule call

### API Endpoints
- `GET /api/scheduling-options/<coach_id>` - Get scheduling options
- `GET /api/check-availability/<coach_id>` - Check coach availability
- `GET /api/upcoming-calls` - Get user's upcoming calls

## 🔄 Background Tasks

### Notification Scheduler
The system runs background tasks for:
- **Call readiness checks** (every minute)
- **24-hour reminders** (every hour)
- **1-hour reminders** (every 15 minutes)
- **Overdue call marking** (every 30 minutes)
- **Notification cleanup** (daily at 2 AM)

### WebSocket Integration
Real-time updates for:
- **Call status changes**
- **New call notifications**
- **Ready to join alerts**

## 🎯 Business Logic

### Scheduling Rules
1. **Free consultations** are limited to one per student-coach pair
2. **Paid sessions** require active, paid contract
3. **Availability checking** prevents double-booking
4. **Rescheduling** has time-based restrictions
5. **Cancellation** requires reason (optional)

### Timezone Handling
- **All times stored in UTC**
- **User timezone conversion** for display
- **Automatic timezone detection**
- **Timezone-aware scheduling**

### Payment Integration
- **Free consultations** require no payment
- **Paid sessions** require contract payment verification
- **Session billing** handled through existing contract system

## 🚀 Deployment

### Production Setup
1. **Video functionality has been removed from this application**
2. **Run database migration** to create tables
3. **Start notification scheduler** (automatic with app)
4. **Configure email settings** (already done)
5. **Test scheduling flow** with real users

### Monitoring
- **Call success rates**
- **Notification delivery rates**
- **Video call quality metrics**
- **User engagement with scheduling**

## 🎉 Success Metrics

### User Engagement
- **Scheduling completion rate**
- **Call attendance rate**
- **Rescheduling frequency**
- **User satisfaction scores**

### System Performance
- **Notification delivery success**
- **Video call stability**
- **Scheduling system uptime**
- **Response times for API calls**

---

## 🎯 Next Steps

The scheduling system is now **fully functional** and ready for production use. The implementation includes:

✅ **Complete dual scheduling system**  
✅ **Interactive call cards with join buttons**  
✅ **Video functionality removed**  
✅ **Automated notification system**  
✅ **Real-time availability checking**  
✅ **Background task scheduling**  
✅ **Comprehensive error handling**  
✅ **User-friendly interfaces**  

The system automatically adapts to show the appropriate scheduling options based on the student-coach relationship and contract status, providing a seamless experience for both free consultations and paid learning sessions.
