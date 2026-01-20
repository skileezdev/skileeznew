from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .user import UserOut

class LearningRequestBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20)
    budget: Optional[float] = None
    experience_level: Optional[str] = None
    skill_type: str = "short_term"

class LearningRequestCreate(LearningRequestBase):
    pass

class LearningRequestOut(LearningRequestBase):
    id: int
    student_id: int
    is_active: bool
    created_at: datetime
    student: Optional[UserOut] = None

    class Config:
        from_attributes = True

class ProposalBase(BaseModel):
    cover_letter: str = Field(..., min_length=50)
    price_per_session: float
    session_count: int

class ProposalCreate(ProposalBase):
    learning_request_id: int

class ProposalOut(ProposalBase):
    id: int
    coach_id: int
    status: str
    created_at: datetime
    coach: Optional[UserOut] = None

    class Config:
        from_attributes = True

class ContractBase(BaseModel):
    title: str
    price_per_session: float
    total_sessions: int
    status: str = "active"

class ContractOut(ContractBase):
    id: int
    student_id: int
    coach_id: int
    learning_request_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SessionOut(BaseModel):
    id: int
    contract_id: int
    scheduled_at: Optional[datetime] = None
    status: str
    topic: Optional[str] = None

    class Config:
        from_attributes = True
