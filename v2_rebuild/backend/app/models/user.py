from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Date, Text, JSON, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class User(Base):
    __tablename__ = "user"

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
    
    # Mirroring 1:1 V1 Fields
    role_switch_count = Column(Integer, default=0)
    preferred_default_role = Column(String(20))
    stripe_customer_id = Column(String(255))
    last_role_switch = Column(DateTime(timezone=True))
    
    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    coach_profile = relationship("CoachProfile", back_populates="user", uselist=False)
    role_switch_logs = relationship("RoleSwitchLog", back_populates="user")

class StudentProfile(Base):
    __tablename__ = "student_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    bio = Column(Text)
    profile_picture = Column(Text)
    country = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="student_profile")

class CoachProfile(Base):
    __tablename__ = "coach_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    coach_title = Column(String(100))
    bio = Column(Text)
    hourly_rate = Column(Float)
    is_approved = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)
    
    # Mirroring 1:1 V1 Coach Fields
    stripe_account_id = Column(String(255))
    onboarding_step = Column(Integer, default=1)
    total_earnings = Column(Numeric(12, 2), default=0.00)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="coach_profile")
    experience = relationship("Experience", back_populates="coach")
    education = relationship("Education", back_populates="coach")
    portfolio_items = relationship("PortfolioItem", back_populates="coach")

class Experience(Base):
    __tablename__ = "experience"
    id = Column(Integer, primary_key=True)
    coach_profile_id = Column(Integer, ForeignKey("coach_profile.id"), nullable=False)
    title = Column(String(100), nullable=False)
    company = Column(String(100), nullable=False)
    location = Column(String(100))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    
    coach = relationship("CoachProfile", back_populates="experience")

class Education(Base):
    __tablename__ = "education"
    id = Column(Integer, primary_key=True)
    coach_profile_id = Column(Integer, ForeignKey("coach_profile.id"), nullable=False)
    degree = Column(String(100), nullable=False)
    institution = Column(String(100), nullable=False)
    field_of_study = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)
    
    coach = relationship("CoachProfile", back_populates="education")

class PortfolioItem(Base):
    __tablename__ = "portfolio_item"
    id = Column(Integer, primary_key=True)
    coach_profile_id = Column(Integer, ForeignKey("coach_profile.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    url = Column(String(500))
    image_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    coach = relationship("CoachProfile", back_populates="portfolio_items")

class RoleSwitchLog(Base):
    __tablename__ = "role_switch_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    from_role = Column(String(20))
    to_role = Column(String(20), nullable=False)
    switch_reason = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="role_switch_logs")
