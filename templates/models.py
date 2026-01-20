from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import json
import time
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Create the db instance
db = SQLAlchemy(model_class=Base)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_student = db.Column(db.Boolean, default=False)
    is_coach = db.Column(db.Boolean, default=False)
    # New dual-role fields
    current_role = db.Column(db.String(20), default=None)  # 'student' or 'coach'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    role_switch_enabled = db.Column(db.Boolean, default=True)
    last_role_switch = db.Column(db.DateTime)
    role_switch_count = db.Column(db.Integer, default=0)
    preferred_default_role = db.Column(db.String(20))
    
    # Email verification fields
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255))
    token_created_at = db.Column(db.DateTime)
    
    # Email change verification fields
    new_email = db.Column(db.String(120))
    email_change_token = db.Column(db.String(255))
    email_change_token_created_at = db.Column(db.DateTime)
    
    # Stripe customer ID
    stripe_customer_id = db.Column(db.String(255), unique=True)
    
    # Timezone preference
    timezone = db.Column(db.String(50), default='UTC')

    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False)
    coach_profile = db.relationship('CoachProfile', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Dual-role helper methods
    def can_switch_roles(self):
        """Check if user has both roles and can switch"""
        return self.is_student and self.is_coach

    def get_available_roles(self):
        """Get list of available roles for the user"""
        roles = []
        if self.is_student:
            roles.append('student')
        if self.is_coach:
            roles.append('coach')
        return roles

    def get_other_role(self):
        """Get the role opposite to current role"""
        if not self.can_switch_roles():
            return None
        return 'coach' if self.current_role == 'student' else 'student'

    def switch_role(self):
        """Switch to the other role if possible"""
        if not self.can_switch_roles():
            return False

        other_role = self.get_other_role()
        if other_role:
            self.current_role = other_role
            return True
        return False

    def set_initial_role(self):
        """Set initial role based on user's roles"""
        if self.is_coach and not self.is_student:
            self.current_role = 'coach'
        elif self.is_student and not self.is_coach:
            self.current_role = 'student'
        elif self.is_coach and self.is_student:
            # If dual role, default to the role they had first (coach takes precedence)
            self.current_role = 'coach' if self.is_coach else 'student'
    
    def get_notifications(self):
        """Safely get notifications for this user"""
        try:
            from models import Notification
            return Notification.query.filter_by(user_id=self.id).all()
        except Exception:
            return []
    
    def get_coach_availability(self):
        """Safely get coach availability for this user"""
        try:
            from models import CoachAvailability
            return CoachAvailability.query.filter_by(coach_id=self.id).first()
        except Exception:
            return None
    
    def get_booking_rules(self):
        """Safely get booking rules for this user"""
        try:
            from models import BookingRule
            return BookingRule.query.filter_by(coach_id=self.id).all()
        except Exception:
            return []
    
    def get_calendar_integrations(self):
        """Safely get calendar integrations for this user"""
        try:
            from models import CalendarIntegration
            return CalendarIntegration.query.filter_by(coach_id=self.id).all()
        except Exception:
            return []

    def get_role_switch_stats(self):
        """Get role switching statistics for the user"""
        return {
            'total_switches': self.role_switch_count or 0,
            'last_switch': self.last_role_switch,
            'can_switch': self.can_switch_roles(),
            'switch_enabled': self.role_switch_enabled,
            'preferred_role': self.preferred_default_role
        }

    def log_role_switch(self, from_role, to_role, reason=None, ip_address=None, user_agent=None):
        """Log a role switch event"""
        log_entry = RoleSwitchLog(
            user_id=self.id,
            from_role=from_role,
            to_role=to_role,
            switch_reason=reason,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log_entry)

        # Update user stats
        self.last_role_switch = datetime.utcnow()
        self.role_switch_count = (self.role_switch_count or 0) + 1

        return log_entry

    def switch_role_with_validation(self, target_role, reason=None, ip_address=None, user_agent=None):
        """Enhanced role switching with comprehensive validation and logging"""
        from utils import validate_role_switch

        # Validate switch
        is_valid, error_message = validate_role_switch(self, target_role)
        if not is_valid:
            return False, error_message

        current_role = self.current_role

        try:
            # Log the switch
            self.log_role_switch(
                from_role=current_role,
                to_role=target_role,
                reason=reason,
                ip_address=ip_address,
                user_agent=user_agent
            )

            # Perform the switch
            self.current_role = target_role

            db.session.commit()

            role_name = 'Coach' if target_role == 'coach' else 'Student'
            return True, f"Successfully switched to {role_name} mode"

        except Exception as e:
            db.session.rollback()
            return False, f"Error switching roles: {str(e)}"

    def get_role_context(self):
        """Get comprehensive role context for templates"""
        return {
            'current_role': self.current_role,
            'available_roles': self.get_available_roles(),
            'can_switch': self.can_switch_roles(),
            'other_role': self.get_other_role(),
            'role_display': self.current_role.title() if self.current_role else 'No Role',
            'switch_enabled': self.role_switch_enabled,
            'is_dual_role': self.can_switch_roles(),
            'coach_approved': self.coach_profile.is_approved if self.coach_profile else False,
            'student_active': bool(self.student_profile) if self.is_student else False
        }


class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bio = db.Column(db.Text)
    age = db.Column(db.Integer)
    profile_picture = db.Column(db.Text)  # Changed from String(255) to Text for file paths
    country = db.Column(db.String(100))  # Added for privacy system
    preferred_languages = db.Column(db.String(255))  # Keep for backwards compatibility
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    languages = db.relationship('StudentLanguage', backref='student_profile', lazy=True, cascade='all, delete-orphan')

class CoachProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal = db.Column(db.String(50))  # main_income, side_income, no_goal
    coach_title = db.Column(db.String(80))  # Professional headline like "Graphic Design Coach"
    skills = db.Column(db.Text)  # JSON string of skills
    bio = db.Column(db.Text)  # Longer description, 100-5000 characters
    profile_picture = db.Column(db.Text)  # Changed from String(255) to Text for base64 data
    country = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    hourly_rate = db.Column(db.Float)
    is_approved = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    total_earnings = db.Column(db.Float, default=0.0)
    onboarding_step = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Stripe Connect account ID
    stripe_account_id = db.Column(db.String(255), unique=True)

    # Relationships
    experiences = db.relationship('Experience', backref='coach_profile', lazy=True)
    educations = db.relationship('Education', backref='coach_profile', lazy=True)
    languages = db.relationship('Language', backref='coach_profile', lazy=True)
    portfolio_items = db.relationship('PortfolioItem', backref='coach_profile', lazy=True)

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coach_profile_id = db.Column(db.Integer, db.ForeignKey('coach_profile.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coach_profile_id = db.Column(db.Integer, db.ForeignKey('coach_profile.id'), nullable=False)
    institution = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(100))
    field_of_study = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)

class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coach_profile_id = db.Column(db.Integer, db.ForeignKey('coach_profile.id'), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    proficiency = db.Column(db.String(20), nullable=False)  # beginner, intermediate, advanced, native

class StudentLanguage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_profile_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    proficiency = db.Column(db.String(20), nullable=False)  # Basic, Conversational, Fluent, Native

class PortfolioItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coach_profile_id = db.Column(db.Integer, db.ForeignKey('coach_profile.id'), nullable=False)
    category = db.Column(db.String(50), default='work_sample')  # case_study, work_sample, introduction, tutorial, testimonial, other
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    project_links = db.Column(db.Text)  # Multiple URLs separated by newlines (YouTube, Drive, etc.)
    thumbnail_image = db.Column(db.String(500))  # Optional thumbnail/cover image file path
    skills = db.Column(db.String(255))  # comma-separated skills
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LearningRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills_needed = db.Column(db.String(255))
    duration = db.Column(db.String(50))  # e.g., "2 weeks", "1 month"
    budget = db.Column(db.Float)
    experience_level = db.Column(db.String(20))  # beginner, intermediate, expert
    skill_type = db.Column(db.String(20), nullable=False, default='short_term')  # short_term, long_term
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New fields for enhanced learning requests
    preferred_times = db.Column(db.Text)  # JSON string of preferred time slots
    sessions_needed = db.Column(db.Integer)  # Number of sessions required
    timeframe = db.Column(db.String(100))  # e.g., "2 weeks", "1 month", "3 months"
    skill_tags = db.Column(db.Text)  # Comma-separated skill tags

    # Relationships
    proposals = db.relationship('Proposal', backref='learning_request', lazy=True)
    student = db.relationship('User', backref='learning_requests')
    
    # Extension methods
    @property
    def preferred_times_list(self):
        """Convert preferred_times JSON to list"""
        if not self.preferred_times:
            return []
        try:
            return json.loads(self.preferred_times)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def skill_tags_list(self):
        """Convert skill_tags to list"""
        if not self.skill_tags:
            return []
        return [tag.strip() for tag in self.skill_tags.split(',') if tag.strip()]
    
    def get_active_proposals(self):
        """Get all pending proposals for this learning request"""
        return self.proposals.filter_by(status='pending').order_by(Proposal.created_at.desc()).all()
    
    def get_accepted_proposal(self):
        """Get the accepted proposal (contract) for this learning request"""
        return self.proposals.filter_by(status='accepted').first()
    
    def is_contract_active(self):
        """Check if this learning request has an active contract"""
        accepted_proposal = self.get_accepted_proposal()
        if not accepted_proposal:
            return False
        contract = accepted_proposal.get_contract()
        return contract and contract.status == 'active'

class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    learning_request_id = db.Column(db.Integer, db.ForeignKey('learning_request.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cover_letter = db.Column(db.Text, nullable=False)
    session_count = db.Column(db.Integer, nullable=False)
    price_per_session = db.Column(db.Float, nullable=False)
    session_duration = db.Column(db.Integer, nullable=False)  # minutes
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New fields for enhanced proposals
    accepted_at = db.Column(db.DateTime)  # When the proposal was accepted
    accepted_terms = db.Column(db.Text)  # JSON string of accepted terms
    availability_match = db.Column(db.Boolean, default=False)  # Whether coach's availability matches student's preferences
    approach_summary = db.Column(db.Text)  # Coach's approach to teaching
    answers = db.Column(db.Text)  # JSON string of answers to screening questions
    payment_model = db.Column(db.String(20), default='per_session')  # per_session, per_hour
    hourly_rate = db.Column(db.Float)  # Hourly rate if payment_model is per_hour

    # Relationships
    coach = db.relationship('User', backref='proposals')
    contracts = db.relationship('Contract', backref='proposal', cascade='all, delete-orphan')
    
    # Extension methods
    @property
    def accepted_terms_dict(self):
        """Convert accepted_terms JSON to dict"""
        if not self.accepted_terms:
            return {}
        try:
            return json.loads(self.accepted_terms)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def answers_dict(self):
        """Convert answers JSON to dict"""
        if not self.answers:
            return {}
        try:
            return json.loads(self.answers)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def is_contract_created(self):
        """Check if this proposal has been accepted and contract created"""
        return self.status == 'accepted' and self.accepted_at is not None
    
    def get_contract(self):
        """Get the contract associated with this proposal"""
        return Contract.query.filter_by(proposal_id=self.id).first()
    
    def create_contract(self, **contract_data):
        """Create a contract from this accepted proposal"""
        if self.status != 'accepted':
            raise ValueError("Can only create contract from accepted proposal")
        
        # Generate contract number
        contract_number = self._generate_contract_number()
        
        contract = Contract(
            proposal_id=self.id,
            student_id=self.learning_request.student_id,
            coach_id=self.coach_id,
            contract_number=contract_number,
            start_date=contract_data.get('start_date', datetime.utcnow().date()),
            end_date=contract_data.get('end_date'),
            total_sessions=contract_data.get('total_sessions', 1),
            total_amount=contract_data.get('total_sessions', 1) * contract_data.get('rate', 0.00),
            payment_model=self.payment_model or 'per_session',
            rate=contract_data.get('rate', 0.00),
            duration_minutes=contract_data.get('duration_minutes', 60),
            timezone=contract_data.get('timezone', 'UTC'),
            cancellation_policy=contract_data.get('cancellation_policy'),
            learning_outcomes=contract_data.get('learning_outcomes')
        )
        
        db.session.add(contract)
        db.session.commit()
        return contract
    
    def _generate_contract_number(self):
        """Generate unique contract number"""
        from datetime import date
        today = date.today()
        date_str = today.strftime('%Y%m%d')
        
        # Find the next available number for today
        counter = 1
        while True:
            contract_num = f"CTR-{date_str}-{counter:04d}"
            if not Contract.query.filter_by(contract_number=contract_num).first():
                return contract_num
            counter += 1
    
    def get_upcoming_sessions(self):
        """Get upcoming scheduled sessions"""
        return self.sessions.filter(
            Session.status == 'scheduled',
            Session.scheduled_at > datetime.utcnow()
        ).order_by(Session.scheduled_at).all()
    
    def get_completed_sessions(self):
        """Get completed sessions"""
        return self.sessions.filter_by(status='completed').order_by(Session.completed_date).all()

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), nullable=False)
    session_number = db.Column(db.Integer, nullable=False)
    scheduled_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    student_notes = db.Column(db.Text)
    coach_notes = db.Column(db.Text)
    
    # New fields for enhanced session management
    scheduled_at = db.Column(db.DateTime)  # More specific scheduling time
    duration_minutes = db.Column(db.Integer)  # Session duration in minutes
    timezone = db.Column(db.String(50), default='UTC')  # Timezone for the session
    reschedule_requested = db.Column(db.Boolean, default=False)  # Whether reschedule was requested
    reschedule_requested_by = db.Column(db.String(20))  # 'student' or 'coach'
    reschedule_reason = db.Column(db.Text)  # Reason for reschedule request
    reschedule_deadline = db.Column(db.DateTime)  # Deadline to respond to reschedule request
    confirmed_by_coach = db.Column(db.Boolean, default=False)  # Whether coach confirmed the session
    
    # Video session fields
    video_started_at = db.Column(db.DateTime)  # When video session started
    video_ended_at = db.Column(db.DateTime)  # When video session ended
    
    # Calendly-like fields for automatic meeting activation
    auto_activated = db.Column(db.Boolean, default=False)  # Whether meeting was auto-activated
    reminder_sent = db.Column(db.Boolean, default=False)  # Whether reminder was sent
    early_join_enabled = db.Column(db.Boolean, default=True)  # Allow early join (5-10 min before)
    buffer_minutes = db.Column(db.Integer, default=0)  # Buffer time before/after meeting
    meeting_started_at = db.Column(db.DateTime)  # When meeting actually started
    meeting_ended_at = db.Column(db.DateTime)  # When meeting actually ended
    waiting_room_enabled = db.Column(db.Boolean, default=True)  # Enable waiting room
    calendar_event_id = db.Column(db.String(255))  # External calendar event ID
    calendar_provider = db.Column(db.String(50))  # 'google', 'outlook', etc.

    # Relationships
    proposal = db.relationship('Proposal', backref='sessions')
    
    def get_contract(self):
        """Safely get the contract associated with this session"""
        if not self.proposal:
            return None
        
        # Query directly to avoid relationship issues
        from models import Contract
        contract = Contract.query.filter_by(proposal_id=self.proposal.id).first()
        return contract
    
    # Extension methods
    def is_reschedule_allowed(self):
        """Check if reschedule is allowed based on 10-hour rule"""
        if not self.scheduled_at:
            return False
        
        # Convert to UTC if timezone is specified
        scheduled_utc = self.scheduled_at
        if self.timezone and self.timezone != 'UTC':
            # Simple timezone conversion (for MVP, assume common timezones)
            # In production, use pytz or similar for proper timezone handling
            pass
        
        cutoff_time = scheduled_utc - timedelta(hours=10)
        return datetime.utcnow() < cutoff_time
    
    def can_request_reschedule(self, user_role):
        """Check if user can request reschedule"""
        if self.status != 'scheduled':
            return False
        
        # Check if there's already a pending reschedule request
        if self.reschedule_requested:
            return False
        
        # If within 10 hours, only student can request
        if not self.is_reschedule_allowed():
            return user_role == 'student'
        
        return True
    
    def request_reschedule(self, requested_by, reason):
        """Request a reschedule with enhanced validation"""
        if not self.can_request_reschedule(requested_by):
            raise ValueError("Reschedule not allowed at this time")
        
        if not reason or not reason.strip():
            raise ValueError("Reason is required for reschedule request")
        
        # Validate reason length
        if len(reason.strip()) < 10:
            raise ValueError("Reschedule reason must be at least 10 characters")
        
        if len(reason.strip()) > 500:
            raise ValueError("Reschedule reason must be less than 500 characters")
        
        self.reschedule_requested = True
        self.reschedule_requested_by = requested_by
        self.reschedule_reason = reason.strip()
        self.reschedule_deadline = datetime.utcnow() + timedelta(hours=24)  # 24 hours to respond
        
        db.session.commit()
    
    def approve_reschedule(self, new_scheduled_at):
        """Approve reschedule request with validation"""
        if not self.reschedule_requested:
            raise ValueError("No reschedule request pending")
        
        # Validate new scheduled time
        if not new_scheduled_at:
            raise ValueError("New scheduled time is required")
        
        # Ensure new time is in the future
        if isinstance(new_scheduled_at, str):
            try:
                new_scheduled_at = datetime.strptime(new_scheduled_at, '%Y-%m-%dT%H:%M')
            except ValueError:
                raise ValueError("Invalid datetime format")
        
        if new_scheduled_at <= datetime.utcnow():
            raise ValueError("New scheduled time must be in the future")
        
        # Ensure new time is at least 1 hour in the future
        if new_scheduled_at <= datetime.utcnow() + timedelta(hours=1):
            raise ValueError("New scheduled time must be at least 1 hour in the future")
        
        self.scheduled_at = new_scheduled_at
        self.reschedule_requested = False
        self.reschedule_requested_by = None
        self.reschedule_reason = None
        self.reschedule_deadline = None
        
        db.session.commit()
    
    def decline_reschedule(self):
        """Decline reschedule request"""
        if not self.reschedule_requested:
            raise ValueError("No reschedule request pending")
        
        self.reschedule_requested = False
        self.reschedule_requested_by = None
        self.reschedule_reason = None
        self.reschedule_deadline = None
        
        db.session.commit()
    
    def mark_completed(self, notes=None, completed_by='coach'):
        """Mark session as completed with enhanced validation"""
        if self.status != 'scheduled':
            raise ValueError("Can only complete scheduled sessions")
        
        # Validate completed_by parameter
        if completed_by not in ['coach', 'student']:
            raise ValueError("completed_by must be 'coach' or 'student'")
        
        # Validate notes length if provided
        if notes and len(notes.strip()) > 1000:
            raise ValueError("Notes must be less than 1000 characters")
        
        self.status = 'completed'
        self.completed_date = datetime.utcnow()
        
        if completed_by == 'coach':
            self.coach_notes = notes.strip() if notes else None
        else:
            self.student_notes = notes.strip() if notes else None
        
        # Update contract completed sessions count
        contract = self.proposal.get_contract()
        if contract:
            contract.completed_sessions += 1
            if contract.completed_sessions >= contract.total_sessions:
                contract.status = 'completed'
        
        db.session.commit()
    
    def mark_missed(self):
        """Mark session as missed with validation"""
        if self.status != 'scheduled':
            raise ValueError("Can only mark scheduled sessions as missed")
        
        # Check if session is actually in the past
        if self.scheduled_at and self.scheduled_at > datetime.utcnow():
            raise ValueError("Cannot mark future sessions as missed")
        
        self.status = 'missed'
        db.session.commit()
    
    def cancel_session(self):
        """Cancel a session with validation"""
        if self.status != 'scheduled':
            raise ValueError("Can only cancel scheduled sessions")
        
        self.status = 'cancelled'
        db.session.commit()
    
    def get_status_display(self):
        """Get human-readable status with additional context"""
        if self.status == 'scheduled':
            if self.reschedule_requested:
                return 'Reschedule Requested'
            elif self.confirmed_by_coach:
                return 'Confirmed'
            else:
                return 'Scheduled'
        elif self.status == 'completed':
            return 'Completed'
        elif self.status == 'cancelled':
            return 'Cancelled'
        elif self.status == 'missed':
            return 'Missed'
        else:
            return self.status.title()
    
    def get_time_until_session(self):
        """Get time remaining until session (for scheduled sessions)"""
        if self.status != 'scheduled' or not self.scheduled_at:
            return None
        
        time_diff = self.scheduled_at - datetime.utcnow()
        if time_diff.total_seconds() <= 0:
            return "Session time has passed"
        
        days = time_diff.days
        hours = time_diff.seconds // 3600
        minutes = (time_diff.seconds % 3600) // 60
        
        if days > 0:
            return f"{days} day(s), {hours} hour(s)"
        elif hours > 0:
            return f"{hours} hour(s), {minutes} minute(s)"
        else:
            return f"{minutes} minute(s)"
    
    def is_overdue(self):
        """Check if session is overdue (past scheduled time but still scheduled)"""
        if self.status != 'scheduled' or not self.scheduled_at:
            return False
        
        return self.scheduled_at < datetime.utcnow()
    
    def can_be_completed(self):
        """Check if session can be marked as completed"""
        return self.status == 'scheduled' and self.scheduled_at and self.scheduled_at <= datetime.utcnow()
    
    # Calendly-like methods for automatic meeting activation
    def can_auto_activate(self):
        """Check if meeting can be auto-activated at scheduled time"""
        if self.status != 'scheduled':
            return False
        
        if not self.scheduled_at:
            return False
        
        # Check if it's time to auto-activate (scheduled time has passed or within 5 minutes before)
        now = datetime.utcnow()
        time_diff = (self.scheduled_at - now).total_seconds()
        return time_diff <= 300  # 5 minutes before or anytime after scheduled time
    
    def auto_activate_meeting(self):
        """Auto-activate the meeting at scheduled time"""
        if not self.can_auto_activate():
            return False
        
        self.auto_activated = True
        self.meeting_started_at = datetime.utcnow()
        self.status = 'active'
        

        
        db.session.commit()
        return True
    
    def can_join_early(self):
        """Check if participants can join early (5-10 minutes before)"""
        if not self.early_join_enabled:
            return False
        
        if self.status != 'scheduled':
            return False
        
        if not self.scheduled_at:
            return False
        
        now = datetime.utcnow()
        time_diff = (self.scheduled_at - now).total_seconds()
        return 0 <= time_diff <= 600  # 10 minutes before
    
    def should_send_reminder(self):
        """Check if reminder should be sent (15-30 minutes before)"""
        if self.reminder_sent:
            return False
        
        if self.status != 'scheduled':
            return False
        
        if not self.scheduled_at:
            return False
        
        now = datetime.utcnow()
        time_diff = (self.scheduled_at - now).total_seconds()
        return 900 <= time_diff <= 1800  # 15-30 minutes before
    
    def mark_reminder_sent(self):
        """Mark that reminder has been sent"""
        self.reminder_sent = True
        db.session.commit()
    
    def get_meeting_duration(self):
        """Get actual meeting duration in minutes"""
        if not self.meeting_started_at:
            return None
        
        end_time = self.meeting_ended_at or datetime.utcnow()
        duration = (end_time - self.meeting_started_at).total_seconds() / 60
        return int(duration)
    
    def end_meeting(self):
        """End the meeting and clean up"""
        if self.status != 'active':
            return False
        
        self.meeting_ended_at = datetime.utcnow()
        self.status = 'completed'
        self.completed_date = datetime.utcnow()
        

        
        db.session.commit()
        return True

    def start_meeting(self):
        """Start the meeting (video functionality removed)"""
        if self.status != 'scheduled':
            return False
        
        try:
            # Update session status to active
            self.status = 'active'
            self.meeting_started_at = datetime.utcnow()
            self.video_started_at = datetime.utcnow()
            

            
            db.session.commit()
            return True
            
        except Exception as e:
            # Rollback on error
            db.session.rollback()
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to start meeting for session {self.id}: {e}")
            return False

    def can_join_session(self):
        """Check if the session can be joined (is active or can join early)"""
        # Can join if session is active
        if self.status == 'active':
            return True
        
        # Can join early if enabled and within time window
        if self.can_join_early():
            return True
        
        return False

class Contract(db.Model):
    """Contract model for managing learning agreements"""
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contract_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), default='awaiting_response')  # awaiting_response, accepted, active, completed, cancelled, disputed
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)  # Optional end date
    total_sessions = db.Column(db.Integer, nullable=False)
    completed_sessions = db.Column(db.Integer, default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(10, 2), default=0.00)
    payment_model = db.Column(db.String(20), nullable=False)  # per_session, per_hour
    rate = db.Column(db.Numeric(10, 2), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)  # Duration of each session in minutes
    timezone = db.Column(db.String(50), default='UTC')
    cancellation_policy = db.Column(db.Text)
    learning_outcomes = db.Column(db.Text)
    
    # Payment fields
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    stripe_payment_intent_id = db.Column(db.String(255))
    payment_date = db.Column(db.DateTime)
    
    # Contract status tracking fields
    accepted_at = db.Column(db.DateTime)  # When coach accepts the contract
    declined_at = db.Column(db.DateTime)  # When coach declines the contract
    payment_completed_at = db.Column(db.DateTime)  # When student completes payment
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # proposal relationship is handled by the backref in Proposal model
    student = db.relationship('User', foreign_keys=[student_id], backref='student_contracts')
    coach = db.relationship('User', foreign_keys=[coach_id], backref='coach_contracts')
    session_payments = db.relationship('SessionPayment', backref='contract', lazy=True)
    
    def get_progress_percentage(self):
        """Get completion percentage"""
        if self.total_sessions == 0:
            return 0
        return (self.completed_sessions / self.total_sessions) * 100
    
    def get_remaining_sessions(self):
        """Get number of remaining sessions"""
        return self.total_sessions - self.completed_sessions
    
    def get_next_session(self):
        """Get the next scheduled session"""
        return Session.query.filter_by(
            proposal_id=self.proposal_id,
            status='scheduled'
        ).filter(Session.scheduled_at > datetime.utcnow()).order_by(Session.scheduled_at).first()
    
    def get_all_sessions(self):
        """Get all sessions for this contract"""
        sessions = Session.query.filter_by(proposal_id=self.proposal_id).all()
        
        # Sort sessions properly handling None values
        sessions_with_date = [s for s in sessions if s.scheduled_at is not None]
        sessions_without_date = [s for s in sessions if s.scheduled_at is None]
        
        # Sort sessions with dates
        sessions_with_date.sort(key=lambda x: x.scheduled_at)
        
        # Combine: sessions with dates first, then sessions without dates
        return sessions_with_date + sessions_without_date
    
    def can_be_cancelled(self):
        """Check if contract can be cancelled"""
        return self.status == 'active' and self.completed_sessions == 0
    
    def cancel(self, reason=None):
        """Cancel the contract"""
        if not self.can_be_cancelled():
            raise ValueError("Contract cannot be cancelled")
        
        self.status = 'cancelled'
        # Cancel all scheduled sessions
        for session in self.get_all_sessions():
            if session.status == 'scheduled':
                session.status = 'cancelled'
        
        db.session.commit()
    
    def mark_payment_paid(self, stripe_payment_intent_id=None):
        """Mark contract payment as paid"""
        self.payment_status = 'paid'
        self.payment_date = datetime.utcnow()
        if stripe_payment_intent_id:
            self.stripe_payment_intent_id = stripe_payment_intent_id
        self.activate_contract()  # Activate contract after payment
    
    def mark_payment_failed(self):
        """Mark contract payment as failed"""
        self.payment_status = 'failed'
        db.session.commit()
    
    def can_schedule_sessions(self):
        """Check if sessions can be scheduled (payment must be paid)"""
        # Log the current state for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Contract {self.id} can_schedule_sessions check: payment_status={self.payment_status}, status={self.status}")
        
        return self.payment_status == 'paid' and self.status == 'active'
    
    def can_be_paid(self):
        """Check if contract can be paid (status is 'accepted' and payment_status is 'pending')"""
        return self.status == 'accepted' and self.payment_status == 'pending'
    
    def activate_contract(self):
        """Activate the contract after payment is completed"""
        if self.payment_status != 'paid':
            raise ValueError("Contract cannot be activated - payment not completed")
        
        self.status = 'active'
        db.session.commit()
    
    def get_payment_amount(self):
        """Get the total payment amount for this contract"""
        return self.total_amount
    
    def fix_status_if_needed(self):
        """Fix contract status if payment is paid but status is not active"""
        if self.payment_status == 'paid' and self.status != 'active':
            self.status = 'active'
            db.session.commit()
            return True
        return False
    
    def get_status_info(self):
        """Get detailed status information for debugging"""
        return {
            'contract_id': self.id,
            'contract_number': self.contract_number,
            'status': self.status,
            'payment_status': self.payment_status,
            'can_schedule_sessions': self.can_schedule_sessions(),
            'total_sessions': self.total_sessions,
            'completed_sessions': self.completed_sessions,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'paid_amount': float(self.paid_amount) if self.paid_amount else 0
        }



class SessionPayment(db.Model):
    """Session payment tracking for Stripe integration (Phase 2)"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    stripe_payment_intent_id = db.Column(db.String(255))
    stripe_transfer_id = db.Column(db.String(255))
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    session = db.relationship('Session', backref='payments', uselist=False)
    
    def mark_paid(self, stripe_transfer_id=None):
        """Mark payment as paid"""
        self.status = 'paid'
        self.paid_at = datetime.utcnow()
        if stripe_transfer_id:
            self.stripe_transfer_id = stripe_transfer_id
        
        # Update contract paid amount
        self.contract.paid_amount += self.amount
        db.session.commit()
    
    def mark_failed(self):
        """Mark payment as failed"""
        self.status = 'failed'
        db.session.commit()
    
    def refund(self):
        """Mark payment as refunded"""
        self.status = 'refunded'
        # Update contract paid amount
        self.contract.paid_amount -= self.amount
        db.session.commit()

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    # New role-based messaging fields
    sender_role = db.Column(db.String(20))  # 'student' or 'coach'
    recipient_role = db.Column(db.String(20))  # 'student' or 'coach'
    message_type = db.Column(db.String(20), default='TEXT')  # TEXT, CONTRACT_OFFER, SYSTEM, CALL_SCHEDULED, FREE_CONSULTATION, SESSION_SCHEDULED
    call_id = db.Column(db.Integer, db.ForeignKey('scheduled_call.id'), nullable=True)  # Link to call for CALL_SCHEDULED messages
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    call = db.relationship('ScheduledCall', backref='messages')
    
    def get_call(self):
        """
        Get the call associated with this message (supports CALL_SCHEDULED, FREE_CONSULTATION, SESSION_SCHEDULED)
        """
        if self.message_type in ['CALL_SCHEDULED', 'FREE_CONSULTATION', 'SESSION_SCHEDULED']:
            # First try to use the direct relationship
            if self.call_id and self.call:
                return self.call
            
            # For FREE_CONSULTATION and SESSION_SCHEDULED messages, try to parse JSON content
            if self.message_type in ['FREE_CONSULTATION', 'SESSION_SCHEDULED']:
                import json
                try:
                    content_data = json.loads(self.content)
                    consultation_id = content_data.get('consultation_id') or content_data.get('session_id')
                    
                    if consultation_id:
                        from models import ScheduledCall
                        call = ScheduledCall.query.get(consultation_id)
                        if call:
                            return call
                except (json.JSONDecodeError, KeyError):
                    pass
            
            # Fallback to the old pattern matching method for backward compatibility
            from datetime import datetime
            import re
            
            # Extract date and time from message content
            pattern = r'(\d+)-minute (\w+(?:\s+\w+)*) scheduled for (.+) \(UTC\)'
            match = re.search(pattern, self.content)
            
            if match:
                duration = int(match.group(1))
                call_type = match.group(2).replace(' ', '_')
                scheduled_str = match.group(3)
                
                try:
                    # Parse the scheduled date
                    scheduled_at = datetime.strptime(scheduled_str, '%B %d, %Y at %I:%M %p')
                    
                    # Find the call that matches these criteria
                    from models import ScheduledCall
                    call = ScheduledCall.query.filter_by(
                        student_id=self.sender_id,
                        coach_id=self.recipient_id,
                        duration_minutes=duration,
                        call_type=call_type,
                        scheduled_at=scheduled_at
                    ).first()
                    
                    return call
                except ValueError:
                    pass
        
        return None

class SavedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    learning_request_id = db.Column(db.Integer, db.ForeignKey('learning_request.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    coach = db.relationship('User', backref='saved_jobs')
    learning_request = db.relationship('LearningRequest', backref='saved_by')

class ScreeningQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    learning_request_id = db.Column(db.Integer, db.ForeignKey('learning_request.id'), nullable=False)
    question_text = db.Column(db.String(250), nullable=False)  # Max 250 characters as per requirement
    order_index = db.Column(db.Integer, nullable=False)  # To maintain question order
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    learning_request = db.relationship('LearningRequest', backref='screening_questions')

class ScreeningAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    screening_question_id = db.Column(db.Integer, db.ForeignKey('screening_question.id'), nullable=False)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    screening_question = db.relationship('ScreeningQuestion', backref='answers')
    proposal = db.relationship('Proposal', backref='screening_answers')

class RoleSwitchLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    from_role = db.Column(db.String(20))  # Previous role
    to_role = db.Column(db.String(20), nullable=False)  # New role
    switch_reason = db.Column(db.String(100))  # Why the switch occurred
    ip_address = db.Column(db.String(45))  # For security tracking
    user_agent = db.Column(db.String(500))  # Browser/device info
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='role_switch_logs')

class ActiveRoleSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    active_role = db.Column(db.String(20), nullable=False)  # Current active role
    session_start = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))

    # Relationships
    user = db.relationship('User', backref='active_role_sessions')

# Utility functions for the contract system
def create_contract_from_proposal(proposal_id, **contract_data):
    """Create a contract from an accepted proposal"""
    proposal = Proposal.query.get_or_404(proposal_id)
    return proposal.create_contract(**contract_data)

def get_user_active_contracts(user_id, role):
    """Get active contracts for a user"""
    if role == 'student':
        return Contract.query.filter_by(student_id=user_id, status='active').all()
    elif role == 'coach':
        return Contract.query.filter_by(coach_id=user_id, status='active').all()
    return []

def get_user_upcoming_sessions(user_id, role):
    """Get upcoming sessions for a user"""
    if role == 'student':
        return Session.query.join(Contract).filter(
            Contract.student_id == user_id,
            Session.status == 'scheduled',
            Session.scheduled_at > datetime.utcnow()
        ).order_by(Session.scheduled_at).all()
    elif role == 'coach':
        return Session.query.join(Contract).filter(
            Contract.coach_id == user_id,
            Session.status == 'scheduled',
            Session.scheduled_at > datetime.utcnow()
        ).order_by(Session.scheduled_at).all()
    return []

def check_missed_sessions():
    """Check for and mark missed sessions (run via cron)"""
    missed_sessions = Session.query.filter(
        Session.status == 'scheduled',
        Session.scheduled_at < datetime.utcnow() - timedelta(minutes=30)
    ).all()
    
    for session in missed_sessions:
        session.mark_missed()
    
    return len(missed_sessions)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'contract', 'session', 'message', 'system'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional fields for linking to specific content
    related_id = db.Column(db.Integer)  # ID of related contract, session, etc.
    related_type = db.Column(db.String(50))  # Type of related content
    
    # Relationship - no backref to avoid SQLAlchemy issues when table doesn't exist
    user = db.relationship('User')
    
    def to_dict(self):
        """Convert notification to dictionary for JSON responses"""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'related_id': self.related_id,
            'related_type': self.related_type
        }
    
    @classmethod
    def create_notification(cls, user_id, title, message, notification_type, related_id=None, related_type=None):
        """Create a new notification"""
        notification = cls(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            related_id=related_id,
            related_type=related_type
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @classmethod
    def get_unread_count(cls, user_id):
        """Get count of unread notifications for a user"""
        return cls.query.filter_by(user_id=user_id, is_read=False).count()
    
    @classmethod
    def get_recent_notifications(cls, user_id, limit=10):
        """Get recent notifications for a user"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def mark_as_read(cls, notification_id, user_id):
        """Mark a specific notification as read"""
        notification = cls.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False
    
    @classmethod
    def mark_all_as_read(cls, user_id):
        """Mark all notifications as read for a user"""
        cls.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()

# ============================================================================
# ENTERPRISE SCHEDULING SYSTEM MODELS
# ============================================================================

class CoachAvailability(db.Model):
    """Coach availability schedule management"""
    id = db.Column(db.Integer, primary_key=True)
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Availability settings
    is_available = db.Column(db.Boolean, default=True)  # Global availability toggle
    timezone = db.Column(db.String(50), default='UTC')
    
    # Working hours (stored as minutes from midnight)
    monday_start = db.Column(db.Integer, default=540)  # 9:00 AM
    monday_end = db.Column(db.Integer, default=1020)   # 5:00 PM
    tuesday_start = db.Column(db.Integer, default=540)
    tuesday_end = db.Column(db.Integer, default=1020)
    wednesday_start = db.Column(db.Integer, default=540)
    wednesday_end = db.Column(db.Integer, default=1020)
    thursday_start = db.Column(db.Integer, default=540)
    thursday_end = db.Column(db.Integer, default=1020)
    friday_start = db.Column(db.Integer, default=540)
    friday_end = db.Column(db.Integer, default=1020)
    saturday_start = db.Column(db.Integer, default=540)
    saturday_end = db.Column(db.Integer, default=1020)
    sunday_start = db.Column(db.Integer, default=540)
    sunday_end = db.Column(db.Integer, default=1020)
    
    # Session settings
    session_duration = db.Column(db.Integer, default=60)  # Default session duration in minutes
    buffer_before = db.Column(db.Integer, default=0)  # Buffer time before sessions in minutes
    buffer_after = db.Column(db.Integer, default=15)  # Buffer time after sessions in minutes
    
    # Booking settings
    advance_booking_days = db.Column(db.Integer, default=30)  # How many days in advance bookings can be made
    same_day_booking = db.Column(db.Boolean, default=False)  # Allow same-day bookings
    instant_confirmation = db.Column(db.Boolean, default=True)  # Auto-confirm bookings
    
    # Pre-contract consultation settings
    consultation_duration = db.Column(db.Integer, default=15)  # Free consultation duration
    consultation_available = db.Column(db.Boolean, default=True)  # Offer free consultations
    consultation_advance_hours = db.Column(db.Integer, default=2)  # Hours in advance for consultation booking
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - no backref to avoid SQLAlchemy issues when table doesn't exist
    coach = db.relationship('User')
    exceptions = db.relationship('AvailabilityException', backref='availability', lazy=True)
    
    def get_working_hours(self, day_of_week):
        """Get working hours for a specific day (0=Monday, 6=Sunday)"""
        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if day_of_week < 0 or day_of_week > 6:
            return None, None
        
        day = day_names[day_of_week]
        start = getattr(self, f'{day}_start')
        end = getattr(self, f'{day}_end')
        return start, end
    
    def is_working_day(self, day_of_week):
        """Check if a day is a working day"""
        start, end = self.get_working_hours(day_of_week)
        return start is not None and end is not None and start < end
    
    def get_available_slots(self, date, duration_minutes=None):
        """Get available time slots for a specific date"""
        if not self.is_available:
            return []
        
        # Get day of week (0=Monday, 6=Sunday)
        day_of_week = date.weekday()
        start_minutes, end_minutes = self.get_working_hours(day_of_week)
        
        if not self.is_working_day(day_of_week):
            return []
        
        # Check for exceptions
        exceptions = [ex for ex in self.exceptions if ex.date == date]
        if any(ex.is_blocked for ex in exceptions):
            return []
        
        # Use session duration or default
        duration = duration_minutes or self.session_duration
        
        # Generate time slots
        slots = []
        current_time = start_minutes
        
        while current_time + duration <= end_minutes:
            slot_start = datetime.combine(date, datetime.min.time()) + timedelta(minutes=current_time)
            slot_end = slot_start + timedelta(minutes=duration)
            
            # Check if slot conflicts with exceptions
            slot_conflicts = False
            for exception in exceptions:
                if exception.overlaps_with(slot_start, slot_end):
                    slot_conflicts = True
                    break
            
            if not slot_conflicts:
                slots.append({
                    'start': slot_start,
                    'end': slot_end,
                    'available': True
                })
            
            current_time += duration + self.buffer_after
        
        return slots

class AvailabilityException(db.Model):
    """Exceptions to regular availability (blocked time, special hours, etc.)"""
    id = db.Column(db.Integer, primary_key=True)
    availability_id = db.Column(db.Integer, db.ForeignKey('coach_availability.id'), nullable=False)
    
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)  # If None, whole day
    end_time = db.Column(db.Time)    # If None, whole day
    is_blocked = db.Column(db.Boolean, default=True)  # True = blocked, False = available
    reason = db.Column(db.String(255))  # Reason for exception
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def overlaps_with(self, start_datetime, end_datetime):
        """Check if this exception overlaps with a time range"""
        exception_start = datetime.combine(self.date, self.start_time or datetime.min.time())
        exception_end = datetime.combine(self.date, self.end_time or datetime.max.time())
        
        return start_datetime < exception_end and end_datetime > exception_start

class BookingRule(db.Model):
    """Scheduling policies and rules"""
    id = db.Column(db.Integer, primary_key=True)
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Booking policies
    cancellation_hours = db.Column(db.Integer, default=24)  # Hours before session for cancellation
    reschedule_hours = db.Column(db.Integer, default=12)    # Hours before session for reschedule
    no_show_policy = db.Column(db.String(50), default='charge_full')  # charge_full, charge_partial, no_charge
    
    # Payment policies
    require_payment_before = db.Column(db.Boolean, default=True)  # Require payment before booking
    allow_partial_payment = db.Column(db.Boolean, default=False)  # Allow partial payments
    
    # Notification settings
    send_reminder_hours = db.Column(db.Integer, default=24)  # Hours before session to send reminder
    send_confirmation = db.Column(db.Boolean, default=True)  # Send booking confirmation
    send_cancellation = db.Column(db.Boolean, default=True)  # Send cancellation notifications
    
    # Calendar integration
    sync_with_calendar = db.Column(db.Boolean, default=False)
    calendar_provider = db.Column(db.String(50))  # google, outlook, etc.
    calendar_id = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - no backref to avoid SQLAlchemy issues when table doesn't exist
    coach = db.relationship('User')

class ScheduledSession(db.Model):
    """Enhanced session scheduling with availability checking"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Session details
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Scheduling details
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Session type
    session_type = db.Column(db.String(50), default='paid')  # paid, consultation, trial
    is_consultation = db.Column(db.Boolean, default=False)  # Free consultation session
    
    # Status tracking
    status = db.Column(db.String(50), default='scheduled')  # scheduled, confirmed, started, completed, cancelled, no_show
    confirmed_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    # Payment tracking
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, refunded
    payment_amount = db.Column(db.Numeric(10, 2))
    stripe_payment_intent_id = db.Column(db.String(255))
    
    # Video session fields
    video_started_at = db.Column(db.DateTime)
    video_ended_at = db.Column(db.DateTime)
    
    # Rescheduling
    reschedule_requested = db.Column(db.Boolean, default=False)
    reschedule_requested_by = db.Column(db.String(20))  # student, coach
    reschedule_reason = db.Column(db.Text)
    reschedule_deadline = db.Column(db.DateTime)
    original_scheduled_at = db.Column(db.DateTime)  # Track original time for rescheduling
    
    # Notifications
    reminder_sent = db.Column(db.Boolean, default=False)
    confirmation_sent = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = db.relationship('Session', backref='scheduled_sessions')
    coach = db.relationship('User', foreign_keys=[coach_id], backref='coach_sessions')
    student = db.relationship('User', foreign_keys=[student_id], backref='student_sessions')
    
    def can_be_cancelled(self, user_role):
        """Check if session can be cancelled by user"""
        if self.status not in ['scheduled', 'confirmed']:
            return False
        
        # Get booking rules
        booking_rule = BookingRule.query.filter_by(coach_id=self.coach_id).first()
        if not booking_rule:
            return True  # Default to allowing cancellation
        
        # Check cancellation window
        cancellation_deadline = self.scheduled_at - timedelta(hours=booking_rule.cancellation_hours)
        return datetime.utcnow() < cancellation_deadline
    
    def can_be_rescheduled(self, user_role):
        """Check if session can be rescheduled by user"""
        if self.status not in ['scheduled', 'confirmed']:
            return False
        
        if self.reschedule_requested:
            return False
        
        # Get booking rules
        booking_rule = BookingRule.query.filter_by(coach_id=self.coach_id).first()
        if not booking_rule:
            return True  # Default to allowing reschedule
        
        # Check reschedule window
        reschedule_deadline = self.scheduled_at - timedelta(hours=booking_rule.reschedule_hours)
        return datetime.utcnow() < reschedule_deadline
    
    def request_reschedule(self, requested_by, reason, new_time=None):
        """Request a reschedule"""
        if not self.can_be_rescheduled(requested_by):
            raise ValueError("Reschedule not allowed")
        
        self.reschedule_requested = True
        self.reschedule_requested_by = requested_by
        self.reschedule_reason = reason
        self.reschedule_deadline = datetime.utcnow() + timedelta(hours=24)
        
        if new_time:
            self.original_scheduled_at = self.scheduled_at
            self.scheduled_at = new_time
        
        db.session.commit()
    
    def approve_reschedule(self, new_scheduled_at):
        """Approve reschedule request"""
        if not self.reschedule_requested:
            raise ValueError("No reschedule request pending")
        
        self.original_scheduled_at = self.scheduled_at
        self.scheduled_at = new_scheduled_at
        self.reschedule_requested = False
        self.reschedule_requested_by = None
        self.reschedule_reason = None
        self.reschedule_deadline = None
        
        db.session.commit()
    
    def decline_reschedule(self):
        """Decline reschedule request"""
        if not self.reschedule_requested:
            raise ValueError("No reschedule request pending")
        
        self.reschedule_requested = False
        self.reschedule_requested_by = None
        self.reschedule_reason = None
        self.reschedule_deadline = None
        
        db.session.commit()
    
    def start_video_session(self):
        """Start the video session"""
        if self.status not in ['scheduled', 'confirmed']:
            raise ValueError("Session cannot be started")
        
        self.status = 'started'
        self.started_at = datetime.utcnow()
        self.video_started_at = datetime.utcnow()
        

        
        db.session.commit()
    
    def end_video_session(self):
        """End the video session"""
        if self.status != 'started':
            raise ValueError("Session is not started")
        
        self.video_ended_at = datetime.utcnow()
        db.session.commit()
    
    def complete_session(self, notes=None):
        """Mark session as completed"""
        if self.status not in ['started', 'scheduled', 'confirmed']:
            raise ValueError("Session cannot be completed")
        
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        
        # Update the original session record
        if self.session:
            self.session.mark_completed(notes)
        
        db.session.commit()
    
    def cancel_session(self, reason=None):
        """Cancel the session"""
        if self.status not in ['scheduled', 'confirmed']:
            raise ValueError("Session cannot be cancelled")
        
        self.status = 'cancelled'
        self.cancelled_at = datetime.utcnow()
        
        # Update the original session record
        if self.session:
            self.session.cancel_session()
        
        db.session.commit()

class CalendarIntegration(db.Model):
    """Calendar integration settings for coaches"""
    id = db.Column(db.Integer, primary_key=True)
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Calendar provider settings
    provider = db.Column(db.String(50), nullable=False)  # google, outlook, apple
    calendar_id = db.Column(db.String(255))
    access_token = db.Column(db.Text)  # Encrypted access token
    refresh_token = db.Column(db.Text)  # Encrypted refresh token
    token_expires_at = db.Column(db.DateTime)
    
    # Sync settings
    sync_enabled = db.Column(db.Boolean, default=True)
    sync_direction = db.Column(db.String(20), default='bidirectional')  # one_way, bidirectional
    last_sync_at = db.Column(db.DateTime)
    
    # Calendar selection
    selected_calendars = db.Column(db.Text)  # JSON array of calendar IDs
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - no backref to avoid SQLAlchemy issues when table doesn't exist
    coach = db.relationship('User')

class ScheduledCall(db.Model):
    """Model for scheduled calls (both free consultations and paid sessions)"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    call_type = db.Column(db.String(20), nullable=False)  # 'free_consultation' or 'paid_session'
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=15)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, active, completed, cancelled, missed

    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Call start/end times
    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)
    
    # Rescheduling fields
    rescheduled_from = db.Column(db.Integer, db.ForeignKey('scheduled_call.id'), nullable=True)
    reschedule_reason = db.Column(db.Text)
    
    # Calendly-like fields for automatic meeting activation
    auto_activated = db.Column(db.Boolean, default=False)  # Whether meeting was auto-activated
    reminder_sent = db.Column(db.Boolean, default=False)  # Whether reminder was sent
    early_join_enabled = db.Column(db.Boolean, default=True)  # Allow early join (5-10 min before)
    buffer_minutes = db.Column(db.Integer, default=0)  # Buffer time before/after meeting
    waiting_room_enabled = db.Column(db.Boolean, default=True)  # Enable waiting room
    calendar_event_id = db.Column(db.String(255))  # External calendar event ID
    calendar_provider = db.Column(db.String(50))  # 'google', 'outlook', etc.
    meeting_started_at = db.Column(db.DateTime)  # When meeting actually started
    meeting_ended_at = db.Column(db.DateTime)  # When meeting actually ended
    
    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], backref='scheduled_calls_as_student')
    coach = db.relationship('User', foreign_keys=[coach_id], backref='scheduled_calls_as_coach')
    contract = db.relationship('Contract', backref='scheduled_calls')
    session = db.relationship('Session', backref='scheduled_call')
    
    def __repr__(self):
        return f'<ScheduledCall {self.id}: {self.call_type} at {self.scheduled_at}>'
    
    @property
    def is_free_consultation(self):
        """Check if this is a free consultation call"""
        return self.call_type == 'free_consultation'
    
    @property
    def is_paid_session(self):
        """Check if this is a paid session call"""
        return self.call_type == 'paid_session'
    
    @property
    def is_ready_to_join(self):
        """Check if call is ready to join (within 5 minutes of scheduled time)"""
        if self.status != 'scheduled':
            return False
        
        now = datetime.utcnow()
        time_diff = abs((self.scheduled_at - now).total_seconds())
        return time_diff <= 300  # 5 minutes
    
    @property
    def is_overdue(self):
        """Check if call is overdue (past scheduled time but still scheduled)"""
        if self.status != 'scheduled':
            return False
        return self.scheduled_at < datetime.utcnow()
    
    @property
    def time_until_call(self):
        """Get time remaining until call starts"""
        if self.status != 'scheduled':
            return None
        
        time_diff = self.scheduled_at - datetime.utcnow()
        if time_diff.total_seconds() <= 0:
            return "Call time has passed"
        
        days = time_diff.days
        hours = time_diff.seconds // 3600
        minutes = (time_diff.seconds % 3600) // 60
        
        if days > 0:
            return f"{days} day(s), {hours} hour(s)"
        elif hours > 0:
            return f"{hours} hour(s), {minutes} minute(s)"
        else:
            return f"{minutes} minute(s)"
    
    def can_be_rescheduled(self, user_role):
        """Check if call can be rescheduled based on user role and time"""
        if self.status != 'scheduled':
            return False
        
        # Free consultations can be rescheduled up to 2 hours before
        if self.is_free_consultation:
            cutoff_time = self.scheduled_at - timedelta(hours=2)
            return datetime.utcnow() < cutoff_time
        
        # Paid sessions follow contract rescheduling rules
        if self.contract:
            # Use contract's rescheduling policy
            cutoff_hours = getattr(self.contract, 'reschedule_hours', 12)
            cutoff_time = self.scheduled_at - timedelta(hours=cutoff_hours)
            return datetime.utcnow() < cutoff_time
        
        return True
    
    def start_call(self):
        """Start the call (video functionality removed)"""
        if self.status != 'scheduled':
            raise ValueError("Can only start scheduled calls")
        
        # Generate room name
        room_name = f"call_{self.id}_{int(time.time())}"
        
        self.status = 'active'
        self.started_at = datetime.utcnow()
        
        db.session.commit()
        
        return room_name
    
    def end_call(self):
        """End the call"""
        if self.status != 'active':
            raise ValueError("Can only end active calls")
        
        self.status = 'completed'
        self.ended_at = datetime.utcnow()
        
        db.session.commit()
    
    def cancel_call(self, reason=None):
        """Cancel the call"""
        if self.status not in ['scheduled', 'active']:
            raise ValueError("Can only cancel scheduled or active calls")
        
        self.status = 'cancelled'
        if reason:
            self.notes = f"Cancelled: {reason}"
        
        db.session.commit()
    
    # Calendly-like methods for automatic meeting activation
    def can_auto_activate(self):
        """Check if meeting can be auto-activated at scheduled time"""
        if self.status != 'scheduled':
            return False
        
        if not self.scheduled_at:
            return False
        
        # Check if it's time to auto-activate (scheduled time has passed or within 5 minutes before)
        now = datetime.utcnow()
        time_diff = (self.scheduled_at - now).total_seconds()
        return time_diff <= 300  # 5 minutes before or anytime after scheduled time
    
    def auto_activate_meeting(self):
        """Auto-activate the meeting at scheduled time"""
        if not self.can_auto_activate():
            return False
        
        self.auto_activated = True
        self.meeting_started_at = datetime.utcnow()
        self.status = 'active'
        

        
        db.session.commit()
        return True
    
    def can_join_early(self):
        """Check if participants can join early (5-10 minutes before)"""
        if not self.early_join_enabled:
            return False
        
        if self.status != 'scheduled':
            return False
        
        if not self.scheduled_at:
            return False
        
        now = datetime.utcnow()
        time_diff = (self.scheduled_at - now).total_seconds()
        return 0 <= time_diff <= 600  # 10 minutes before
    
    def should_send_reminder(self):
        """Check if reminder should be sent (15-30 minutes before)"""
        if self.reminder_sent:
            return False
        
        if self.status != 'scheduled':
            return False
        
        if not self.scheduled_at:
            return False
        
        now = datetime.utcnow()
        time_diff = (self.scheduled_at - now).total_seconds()
        return 900 <= time_diff <= 1800  # 15-30 minutes before
    
    def mark_reminder_sent(self):
        """Mark that reminder has been sent"""
        self.reminder_sent = True
        db.session.commit()
    
    def get_meeting_duration(self):
        """Get actual meeting duration in minutes"""
        if not self.meeting_started_at:
            return None
        
        end_time = self.meeting_ended_at or datetime.utcnow()
        duration = (end_time - self.meeting_started_at).total_seconds() / 60
        return int(duration)
    
    def end_meeting(self):
        """End the meeting and clean up"""
        if self.status != 'active':
            return False
        
        self.meeting_ended_at = datetime.utcnow()
        self.status = 'completed'
        self.completed_date = datetime.utcnow()
        

        
        db.session.commit()
        return True
    
    def reschedule_call(self, new_scheduled_at, reason=None):
        """Reschedule the call"""
        if not self.can_be_rescheduled('student'):
            raise ValueError("Call cannot be rescheduled at this time")
        
        # Create new call record
        new_call = ScheduledCall(
            student_id=self.student_id,
            coach_id=self.coach_id,
            call_type=self.call_type,
            scheduled_at=new_scheduled_at,
            duration_minutes=self.duration_minutes,
            contract_id=self.contract_id,
            session_id=self.session_id,
            rescheduled_from=self.id,
            reschedule_reason=reason
        )
        
        # Cancel old call
        self.status = 'cancelled'
        self.notes = f"Rescheduled to {new_scheduled_at}"
        
        db.session.add(new_call)
        db.session.commit()
        
        return new_call

class CallNotification(db.Model):
    """Model for tracking call notifications"""
    id = db.Column(db.Integer, primary_key=True)
    call_id = db.Column(db.Integer, db.ForeignKey('scheduled_call.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # scheduled, reminder_24h, reminder_1h, ready, completed
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_to_student = db.Column(db.Boolean, default=False)
    sent_to_coach = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    notification_sent = db.Column(db.Boolean, default=False)
    
    # Relationships
    call = db.relationship('ScheduledCall', backref='notifications')
    
    def __repr__(self):
        return f'<CallNotification {self.id}: {self.notification_type} for call {self.call_id}>'