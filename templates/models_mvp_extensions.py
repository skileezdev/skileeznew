# MVP Contract System Model Extensions
# These extensions add to the existing models.py without breaking current functionality

from app import db
from datetime import datetime, timedelta
import json

# Extend existing models with new fields and methods

class LearningRequestExtension:
    """Extension methods for LearningRequest model"""
    
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

class ProposalExtension:
    """Extension methods for Proposal model"""
    
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
    
    @property
    def payment_schedule_list(self):
        """Convert payment_schedule JSON to list"""
        if not self.payment_schedule:
            return []
        try:
            return json.loads(self.payment_schedule)
        except (json.JSONDecodeError, TypeError):
            return []
    
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
            total_sessions=self.session_count,
            total_amount=self.total_price,
            payment_model=self.payment_model or 'per_session',
            rate=self.price_per_session if self.payment_model == 'per_session' else self.hourly_rate,
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

class SessionExtension:
    """Extension methods for Session model"""
    
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
        
        # If within 10 hours, only student can request
        if not self.is_reschedule_allowed():
            return user_role == 'student'
        
        return True
    
    def request_reschedule(self, requested_by, reason):
        """Request a reschedule"""
        if not self.can_request_reschedule(requested_by):
            raise ValueError("Reschedule not allowed")
        
        self.reschedule_requested = True
        self.reschedule_requested_by = requested_by
        self.reschedule_reason = reason
        self.reschedule_deadline = datetime.utcnow() + timedelta(hours=24)  # 24 hours to respond
        
        db.session.commit()
    
    def approve_reschedule(self, new_scheduled_at):
        """Approve reschedule request"""
        if not self.reschedule_requested:
            raise ValueError("No reschedule request pending")
        
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
        """Mark session as completed"""
        if self.status != 'scheduled':
            raise ValueError("Can only complete scheduled sessions")
        
        self.status = 'completed'
        self.completed_date = datetime.utcnow()
        
        if completed_by == 'coach':
            self.coach_notes = notes
        else:
            self.student_notes = notes
        
        # Update contract completed sessions count
        contract = self.proposal.get_contract()
        if contract:
            contract.completed_sessions += 1
            if contract.completed_sessions >= contract.total_sessions:
                contract.status = 'completed'
        
        db.session.commit()
    
    def mark_missed(self):
        """Mark session as missed"""
        if self.status != 'scheduled':
            return
        
        self.status = 'missed'
        db.session.commit()

# New models for the contract system

class Contract(db.Model):
    """Contract model for managing learning agreements"""
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contract_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, active, completed, cancelled, declined, disputed
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)  # Optional end date
    total_sessions = db.Column(db.Integer, nullable=False)
    completed_sessions = db.Column(db.Integer, default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(10, 2), default=0.00)
    payment_model = db.Column(db.String(20), nullable=False)  # per_session, per_hour
    rate = db.Column(db.Numeric(10, 2), nullable=False)
    timezone = db.Column(db.String(50), default='UTC')
    cancellation_policy = db.Column(db.Text)
    learning_outcomes = db.Column(db.Text)
    accepted_at = db.Column(db.DateTime)  # When coach accepts the contract
    declined_at = db.Column(db.DateTime)  # When coach declines the contract
    payment_completed_at = db.Column(db.DateTime)  # When student completes payment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    proposal = db.relationship('Proposal', backref='contract', uselist=False)
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
        return Session.query.filter_by(proposal_id=self.proposal_id).order_by(Session.scheduled_at).all()
    
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
