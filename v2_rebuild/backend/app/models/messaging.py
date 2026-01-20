from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    
    # 1:1 Mirror Fields
    sender_role = Column(String(20)) # 'student' or 'coach'
    recipient_role = Column(String(20)) # 'student' or 'coach'
    message_type = Column(String(20), default='TEXT') # TEXT, CONTRACT_OFFER, SYSTEM, CALL_SCHEDULED
    
    # Relationships to calls/sessions
    session_id = Column(Integer, ForeignKey("session.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    recipient = relationship("User", foreign_keys=[recipient_id], backref="received_messages")
    session = relationship("Session", backref="messages")

class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False) # 'contract', 'session', 'message', 'system'
    is_read = Column(Boolean, default=False)
    
    # Polymorphic-ish linking
    related_id = Column(Integer)
    related_type = Column(String(50))
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", backref="notifications")
