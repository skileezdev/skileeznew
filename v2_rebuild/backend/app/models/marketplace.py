from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class LearningRequest(Base):
    __tablename__ = "learning_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    budget = Column(Float)
    experience_level = Column(String(50))
    skill_type = Column(String(50), default='short_term')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    student = relationship("User", backref="learning_requests")
    proposals = relationship("Proposal", back_populates="learning_request")

class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    learning_request_id = Column(Integer, ForeignKey("learning_requests.id"), nullable=False)
    coach_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cover_letter = Column(Text, nullable=False)
    price_per_session = Column(Float, nullable=False)
    session_count = Column(Integer, nullable=False)
    status = Column(String(20), default='pending')  # pending, accepted, rejected
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    learning_request = relationship("LearningRequest", back_populates="proposals")
    coach = relationship("User", backref="proposals")
    contracts = relationship("Contract", back_populates="proposal")

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coach_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default='active')  # active, completed, cancelled
    total_amount = Column(Float)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    proposal = relationship("Proposal", back_populates="contracts")
    sessions = relationship("Session", back_populates="contract")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    session_number = Column(Integer)
    scheduled_at = Column(DateTime(timezone=True))
    status = Column(String(20), default='scheduled') # scheduled, completed, missed, cancelled
    
    contract = relationship("Contract", back_populates="sessions")
