from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    is_student = Column(Boolean, default=False)
    is_coach = Column(Boolean, default=False)
    current_role = Column(String(20), default=None)  # 'student' or 'coach'
    timezone = Column(String(50), default='UTC')
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    email_verified = Column(Boolean, default=False)
    
    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    coach_profile = relationship("CoachProfile", back_populates="user", uselist=False)

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bio = Column(Text)
    profile_picture = Column(Text)
    country = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="student_profile")

class CoachProfile(Base):
    __tablename__ = "coach_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coach_title = Column(String(100))
    bio = Column(Text)
    hourly_rate = Column(Float)
    is_approved = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="coach_profile")
