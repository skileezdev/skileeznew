from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, JSON, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timezone
from .database import Base

class LearningRequest(Base):
    __tablename__ = "learning_request"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    budget = Column(Float)
    experience_level = Column(String(50))
    skill_type = Column(String(50), default='short_term')
    is_active = Column(Boolean, default=True)
    
    # 1:1 Mirror Fields
    preferred_times = Column(JSON) # List of days/times
    sessions_needed = Column(Integer, default=1)
    timeframe = Column(String(50))
    skill_tags = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    student = relationship("User", backref="learning_requests")
    proposals = relationship("Proposal", back_populates="learning_request")
    screening_questions = relationship("ScreeningQuestion", back_populates="learning_request")

class ScreeningQuestion(Base):
    __tablename__ = "screening_question"
    id = Column(Integer, primary_key=True)
    learning_request_id = Column(Integer, ForeignKey("learning_request.id"), nullable=False)
    question_text = Column(String(250), nullable=False)
    order_index = Column(Integer, default=0)
    
    learning_request = relationship("LearningRequest", back_populates="screening_questions")

class Proposal(Base):
    __tablename__ = "proposal"

    id = Column(Integer, primary_key=True, index=True)
    learning_request_id = Column(Integer, ForeignKey("learning_request.id"), nullable=False)
    coach_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cover_letter = Column(Text, nullable=False)
    price_per_session = Column(Float, nullable=False)
    session_count = Column(Integer, nullable=False)
    status = Column(String(20), default='pending')  # pending, accepted, rejected, archived
    
    # 1:1 Mirror Fields
    answers = Column(JSON) # Answers to screening questions
    approach_summary = Column(Text)
    availability_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    learning_request = relationship("LearningRequest", back_populates="proposals")
    coach = relationship("User", backref="proposals")
    contract = relationship("Contract", back_populates="proposal", uselist=False)
    sessions = relationship("Session", back_populates="proposal")

class ScreeningAnswer(Base):
    __tablename__ = "screening_answer"
    id = Column(Integer, primary_key=True)
    proposal_id = Column(Integer, ForeignKey("proposal.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("screening_question.id"), nullable=False)
    answer_text = Column(Text, nullable=False)

class Contract(Base):
    __tablename__ = "contract"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposal.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coach_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contract_number = Column(String(50), unique=True)
    status = Column(String(20), default='awaiting_response')  # awaiting_response, active, completed, cancelled, disputed
    
    # 1:1 Mirror Fields
    total_amount = Column(Numeric(10, 2))
    paid_amount = Column(Numeric(10, 2), default=0.00)
    payment_model = Column(String(20), default='per_session') # per_session, per_hour
    rate = Column(Numeric(10, 2))
    total_sessions = Column(Integer)
    completed_sessions = Column(Integer, default=0)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(50), default='UTC')
    cancellation_policy = Column(Text)
    learning_outcomes = Column(Text)
    
    # Payment Fields
    payment_status = Column(String(20), default='pending') # pending, paid, failed, refunded
    stripe_payment_intent_id = Column(String(255))
    payment_date = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    proposal = relationship("Proposal", back_populates="contract")

class Session(Base):
    __tablename__ = "session"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposal.id"), nullable=False)
    session_number = Column(Integer)
    scheduled_at = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer, default=60)
    status = Column(String(20), default='scheduled') # scheduled, active, completed, missed, cancelled
    
    # 1:1 Mirror Fields (Meeting & Rescheduling)
    meeting_link = Column(String(500))
    meeting_started_at = Column(DateTime(timezone=True))
    meeting_ended_at = Column(DateTime(timezone=True))
    reminder_sent = Column(Boolean, default=False)
    
    reschedule_requested = Column(Boolean, default=False)
    reschedule_requested_by = Column(String(20)) # 'student' or 'coach'
    reschedule_reason = Column(Text)
    reschedule_new_date = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    proposal = relationship("Proposal", back_populates="sessions")

    @property
    def contract(self):
        return self.proposal.contract
