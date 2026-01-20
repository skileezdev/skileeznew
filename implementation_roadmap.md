# Skileez MVP Contract System Implementation Roadmap

## Phase 1: Core Contract System (MVP)

### Step 1: Database Migration & Model Updates
- [x] Create migration file (`migrations/mvp_contract_system.sql`)
- [x] Create model extensions (`models_mvp_extensions.py`)
- [ ] Update existing `models.py` to include new fields
- [ ] Run migration on development database
- [ ] Test model relationships and methods

### Step 2: Enhanced Job Posting Forms
- [ ] Update `LearningRequestForm` in `forms.py`:
  - Add `preferred_times` (JSON field for time preferences)
  - Add `sessions_needed` (Integer field)
  - Add `skill_tags` (String field)
  - Add `timezone` (Select field with common timezones)
- [ ] Update job posting templates:
  - `templates/jobs/post_request.html` - Add new fields
  - `templates/jobs/edit_job.html` - Add new fields
- [ ] Update job posting routes:
  - `POST /api/post-request` - Handle new fields
  - `POST /post-request` - Handle new fields
  - `POST /edit-job/<id>` - Handle new fields

### Step 3: Enhanced Proposal System
- [ ] Update proposal form creation in `routes.py`:
  - Add `approach_summary` field
  - Add `availability_match` checkbox
  - Add `payment_model` selection (per_session/per_hour)
  - Add `hourly_rate` field (conditional on payment_model)
- [ ] Update proposal submission:
  - `POST /submit-proposal/<job_id>` - Handle new fields
  - Store screening question answers in JSON format
- [ ] Update proposal display:
  - `templates/jobs/job_details.html` - Show new fields
  - `templates/jobs/job_management.html` - Show new fields

### Step 4: Contract Creation System
- [ ] Create contract creation routes:
  ```python
  # New routes to add to routes.py
  @app.route('/contracts/create/<int:proposal_id>', methods=['GET', 'POST'])
  @app.route('/contracts/<int:contract_id>', methods=['GET'])
  @app.route('/contracts/<int:contract_id>/cancel', methods=['POST'])
  ```
- [ ] Create contract forms in `forms.py`:
  ```python
  class ContractForm(FlaskForm):
      start_date = DateField('Start Date', validators=[DataRequired()])
      end_date = DateField('End Date', validators=[Optional()])
      timezone = SelectField('Timezone', choices=timezone_choices)
      cancellation_policy = TextAreaField('Cancellation Policy')
      learning_outcomes = TextAreaField('Learning Outcomes')
  ```
- [ ] Update proposal acceptance flow:
  - Modify `POST /accept-proposal/<proposal_id>` to create contract
  - Add contract terms to accepted proposal
  - Redirect to contract details page

### Step 5: Scheduling System
- [ ] Create session management routes:
  ```python
  # New routes to add to routes.py
  @app.route('/contracts/<int:contract_id>/sessions', methods=['GET', 'POST'])
  @app.route('/sessions/<int:session_id>/schedule', methods=['POST'])
  @app.route('/sessions/<int:session_id>/confirm', methods=['POST'])
  @app.route('/sessions/<int:session_id>/reschedule', methods=['POST'])
  @app.route('/sessions/<int:session_id>/approve-reschedule', methods=['POST'])
  @app.route('/sessions/<int:session_id>/decline-reschedule', methods=['POST'])
  @app.route('/sessions/<int:session_id>/complete', methods=['POST'])
  @app.route('/sessions/<int:session_id>/cancel', methods=['POST'])
  ```
- [ ] Create session forms:
  ```python
  class SessionScheduleForm(FlaskForm):
      scheduled_at = DateTimeField('Scheduled Date/Time', validators=[DataRequired()])
      duration_minutes = IntegerField('Duration (minutes)', validators=[DataRequired()])
      timezone = SelectField('Timezone', choices=timezone_choices)
  
  class RescheduleRequestForm(FlaskForm):
      new_scheduled_at = DateTimeField('New Date/Time', validators=[DataRequired()])
      reason = TextAreaField('Reason for Reschedule', validators=[DataRequired()])
  ```
- [ ] Create scheduling templates:
  - `templates/contracts/schedule_session.html`
  - `templates/contracts/session_details.html`
  - `templates/contracts/reschedule_request.html`

### Step 6: Enhanced Dashboards
- [ ] Update student dashboard (`templates/dashboard/student_dashboard.html`):
  - Add "Active Contracts" section
  - Add "Upcoming Sessions" section
  - Add "Contract Progress" cards
- [ ] Update coach dashboard (`templates/dashboard/coach_dashboard.html`):
  - Add "Active Contracts" section
  - Add "Upcoming Sessions" section
  - Add "Earnings Summary" (Phase 1: mock data)
- [ ] Create contract management pages:
  - `templates/contracts/contract_list.html`
  - `templates/contracts/contract_details.html`
  - `templates/contracts/session_list.html`

### Step 7: Messaging Integration
- [ ] Update messaging system to support contract creation:
  - Add "Create Contract" button in chat for accepted proposals
  - Add contract summary display in chat
  - Add session scheduling shortcuts in chat
- [ ] Update message templates:
  - `templates/messages/conversation.html` - Add contract actions
  - `templates/messages/inbox.html` - Add contract indicators

### Step 8: Email Notifications
- [ ] Create email templates for contract events:
  - `templates/emails/contract_created.html`
  - `templates/emails/session_scheduled.html`
  - `templates/emails/reschedule_requested.html`
  - `templates/emails/session_reminder.html`
- [ ] Add email sending functions to `email_utils.py`:
  ```python
  def send_contract_created_email(contract)
  def send_session_scheduled_email(session)
  def send_reschedule_request_email(session)
  def send_session_reminder_email(session)
  ```

## Phase 2: Payment Integration (Future)

### Step 9: Stripe Integration
- [ ] Install Stripe Python library
- [ ] Create Stripe configuration
- [ ] Create payment models and routes
- [ ] Implement payment flow
- [ ] Add webhook handling

## Implementation Details

### API Routes Specification

#### Contract Management
```python
# GET /contracts - List user's contracts
# GET /contracts/<id> - View contract details
# POST /contracts/create/<proposal_id> - Create contract from proposal
# POST /contracts/<id>/cancel - Cancel contract
# GET /contracts/<id>/sessions - List contract sessions
```

#### Session Management
```python
# POST /sessions/<id>/schedule - Schedule a session
# POST /sessions/<id>/confirm - Confirm session (coach)
# POST /sessions/<id>/reschedule - Request reschedule
# POST /sessions/<id>/approve-reschedule - Approve reschedule
# POST /sessions/<id>/decline-reschedule - Decline reschedule
# POST /sessions/<id>/complete - Mark session complete
# POST /sessions/<id>/cancel - Cancel session
```

### Database Schema Updates

#### LearningRequest Table
```sql
ALTER TABLE learning_request ADD COLUMN preferred_times TEXT;
ALTER TABLE learning_request ADD COLUMN sessions_needed INTEGER;
ALTER TABLE learning_request ADD COLUMN skill_tags TEXT;
ALTER TABLE learning_request ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';
```

#### Proposal Table
```sql
ALTER TABLE proposal ADD COLUMN accepted_at TIMESTAMP;
ALTER TABLE proposal ADD COLUMN accepted_terms TEXT;
ALTER TABLE proposal ADD COLUMN availability_match BOOLEAN DEFAULT FALSE;
ALTER TABLE proposal ADD COLUMN approach_summary TEXT;
ALTER TABLE proposal ADD COLUMN answers TEXT;
ALTER TABLE proposal ADD COLUMN payment_model VARCHAR(20) DEFAULT 'per_session';
ALTER TABLE proposal ADD COLUMN hourly_rate DECIMAL(10,2);
ALTER TABLE proposal ADD COLUMN expected_total DECIMAL(10,2);
ALTER TABLE proposal ADD COLUMN payment_schedule TEXT;
```

#### Session Table
```sql
ALTER TABLE session ADD COLUMN scheduled_at TIMESTAMP;
ALTER TABLE session ADD COLUMN duration_minutes INTEGER DEFAULT 60;
ALTER TABLE session ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';
ALTER TABLE session ADD COLUMN reschedule_requested BOOLEAN DEFAULT FALSE;
ALTER TABLE session ADD COLUMN reschedule_requested_by VARCHAR(20);
ALTER TABLE session ADD COLUMN reschedule_reason TEXT;
ALTER TABLE session ADD COLUMN reschedule_deadline TIMESTAMP;
ALTER TABLE session ADD COLUMN confirmed_by_coach BOOLEAN DEFAULT FALSE;
```

### UI Components

#### Contract Cards
```html
<!-- Active Contract Card -->
<div class="contract-card">
  <div class="contract-header">
    <h3>{{ contract.contract_number }}</h3>
    <span class="status-badge">{{ contract.status }}</span>
  </div>
  <div class="contract-progress">
    <div class="progress-bar">
      <div class="progress-fill" style="width: {{ contract.get_progress_percentage() }}%"></div>
    </div>
    <span>{{ contract.completed_sessions }}/{{ contract.total_sessions }} sessions</span>
  </div>
  <div class="contract-actions">
    <a href="{{ url_for('contract_details', contract_id=contract.id) }}" class="btn-primary">View Details</a>
    <a href="{{ url_for('schedule_session', contract_id=contract.id) }}" class="btn-secondary">Schedule Session</a>
  </div>
</div>
```

#### Session Scheduling Form
```html
<form method="POST" action="{{ url_for('schedule_session', contract_id=contract.id) }}">
  {{ form.csrf_token }}
  <div class="form-group">
    {{ form.scheduled_at.label }}
    {{ form.scheduled_at(class="form-control", type="datetime-local") }}
  </div>
  <div class="form-group">
    {{ form.duration_minutes.label }}
    {{ form.duration_minutes(class="form-control") }}
  </div>
  <div class="form-group">
    {{ form.timezone.label }}
    {{ form.timezone(class="form-control") }}
  </div>
  <button type="submit" class="btn-primary">Schedule Session</button>
</form>
```

### Business Logic

#### Reschedule Rules
```python
def can_reschedule_session(session, user_role):
    """Check if session can be rescheduled based on 10-hour rule"""
    if session.status != 'scheduled':
        return False
    
    cutoff_time = session.scheduled_at - timedelta(hours=10)
    
    # If within 10 hours, only student can request
    if datetime.utcnow() >= cutoff_time:
        return user_role == 'student'
    
    return True
```

#### Contract Creation
```python
def create_contract_from_proposal(proposal_id, contract_data):
    """Create contract from accepted proposal"""
    proposal = Proposal.query.get_or_404(proposal_id)
    
    if proposal.status != 'accepted':
        raise ValueError("Can only create contract from accepted proposal")
    
    # Create contract
    contract = Contract(
        proposal_id=proposal.id,
        student_id=proposal.learning_request.student_id,
        coach_id=proposal.coach_id,
        contract_number=generate_contract_number(),
        start_date=contract_data['start_date'],
        total_sessions=proposal.session_count,
        total_amount=proposal.total_price,
        payment_model=proposal.payment_model,
        rate=proposal.price_per_session,
        timezone=contract_data.get('timezone', 'UTC')
    )
    
    db.session.add(contract)
    db.session.commit()
    
    # Send notifications
    send_contract_created_email(contract)
    
    return contract
```

### Testing Strategy

#### Unit Tests
- [ ] Test contract creation from proposal
- [ ] Test session scheduling and rescheduling
- [ ] Test reschedule rules (10-hour cutoff)
- [ ] Test contract status updates
- [ ] Test email notifications

#### Integration Tests
- [ ] Test complete job posting → proposal → acceptance → contract flow
- [ ] Test session scheduling and completion flow
- [ ] Test messaging integration with contracts
- [ ] Test dashboard updates with contracts

#### Manual Testing
- [ ] Test job posting with new fields
- [ ] Test proposal submission with new fields
- [ ] Test contract creation and management
- [ ] Test session scheduling and rescheduling
- [ ] Test email notifications
- [ ] Test dashboard displays

### Deployment Checklist

#### Pre-deployment
- [ ] Run database migration
- [ ] Test all new routes and forms
- [ ] Verify email templates work
- [ ] Check mobile responsiveness
- [ ] Test with existing data

#### Post-deployment
- [ ] Monitor error logs
- [ ] Verify email delivery
- [ ] Check contract creation flow
- [ ] Monitor session scheduling
- [ ] Gather user feedback

### Future Enhancements (Phase 2+)

#### Advanced Features
- [ ] Real-time chat with WebSockets
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Video call integration
- [ ] File sharing in sessions
- [ ] Session recording
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] Mobile app development

#### Payment Features
- [ ] Stripe Connect for coach payouts
- [ ] Escrow system
- [ ] Subscription billing
- [ ] Refund processing
- [ ] Tax reporting
- [ ] Invoice generation

This roadmap provides a comprehensive implementation plan for the MVP contract system while maintaining compatibility with the existing Skileez codebase.
