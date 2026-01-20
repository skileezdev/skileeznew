from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal
from .user import UserOut

class ScreeningQuestionBase(BaseModel):
    question_text: str = Field(..., max_length=250)
    order_index: int = 0

class ScreeningQuestionCreate(ScreeningQuestionBase):
    pass

class ScreeningQuestionOut(ScreeningQuestionBase):
    id: int
    class Config:
        from_attributes = True

class LearningRequestBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20)
    budget: Optional[float] = None
    experience_level: Optional[str] = None
    skill_type: str = "short_term"
    preferred_times: Optional[List[Any]] = None
    sessions_needed: int = 1
    timeframe: Optional[str] = None
    skill_tags: Optional[List[str]] = None

class LearningRequestCreate(LearningRequestBase):
    screening_questions: List[ScreeningQuestionCreate] = []

class LearningRequestOut(LearningRequestBase):
    id: int
    student_id: int
    is_active: bool
    created_at: datetime
    student: Optional[UserOut] = None
    screening_questions: List[ScreeningQuestionOut] = []

    class Config:
        from_attributes = True

class ScreeningAnswerBase(BaseModel):
    question_id: int
    answer_text: str

class ProposalBase(BaseModel):
    cover_letter: str = Field(..., min_length=50)
    price_per_session: float
    session_count: int
    approach_summary: Optional[str] = None
    availability_notes: Optional[str] = None

class ProposalCreate(ProposalBase):
    learning_request_id: int
    answers: List[ScreeningAnswerBase] = []

class ProposalOut(ProposalBase):
    id: int
    coach_id: int
    status: str
    created_at: datetime
    coach: Optional[UserOut] = None
    answers: Optional[List[Any]] = None

    class Config:
        from_attributes = True

class ContractBase(BaseModel):
    proposal_id: int
    status: str = "awaiting_response"
    total_amount: Decimal
    paid_amount: Decimal = Decimal('0.00')
    payment_model: str = "per_session"
    rate: Decimal
    total_sessions: int
    duration_minutes: int = 60
    timezone: str = "UTC"
    cancellation_policy: Optional[str] = None
    learning_outcomes: Optional[str] = None

class ContractOut(ContractBase):
    id: int
    student_id: int
    coach_id: int
    contract_number: Optional[str] = None
    payment_status: str
    created_at: datetime
    completed_sessions: int

    class Config:
        from_attributes = True

class SessionOut(BaseModel):
    id: int
    contract_id: int
    session_number: int
    scheduled_at: Optional[datetime] = None
    duration_minutes: int
    status: str
    meeting_link: Optional[str] = None
    reschedule_requested: bool
    reschedule_requested_by: Optional[str] = None
    reschedule_new_date: Optional[datetime] = None

    class Config:
        from_attributes = True
