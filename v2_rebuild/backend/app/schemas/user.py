from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List, Any
from datetime import datetime, date
from decimal import Decimal

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    timezone: Optional[str] = None
    preferred_default_role: Optional[str] = None

class ExperienceBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None

class ExperienceOut(ExperienceBase):
    id: int
    class Config:
        from_attributes = True

class EducationBase(BaseModel):
    degree: str
    institution: str
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class EducationOut(EducationBase):
    id: int
    class Config:
        from_attributes = True

class PortfolioItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None

class PortfolioItemOut(PortfolioItemBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class StudentProfileOut(BaseModel):
    id: int
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    country: Optional[str] = None
    learning_goals: Optional[List[str]] = []
    interests: Optional[List[str]] = []
    class Config:
        from_attributes = True

class CoachProfileOut(BaseModel):
    id: int
    coach_title: Optional[str] = None
    bio: Optional[str] = None
    hourly_rate: Optional[float] = None
    is_approved: bool
    rating: float
    is_stripe_enabled: bool = False
    tier: str = "standard"
    total_earnings: Decimal = Decimal("0.00")
    experience: List[ExperienceOut] = []
    education: List[EducationOut] = []
    portfolio_items: List[PortfolioItemOut] = []
    class Config:
        from_attributes = True

class UserOut(UserBase):
    id: int
    is_student: bool
    is_coach: bool
    current_role: Optional[str]
    created_at: datetime
    role_switch_count: int
    onboarding_completed: bool = False
    profile_completion_percentage: int = 0
    
    student_profile: Optional[StudentProfileOut] = None
    coach_profile: Optional[CoachProfileOut] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
