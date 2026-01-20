from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1)
    recipient_id: int
    message_type: str = "TEXT"
    sender_role: Optional[str] = "student" # or coach
    recipient_role: Optional[str] = "coach" 
    session_id: Optional[int] = None
    
class MessageCreate(MessageBase):
    pass

class MessageOut(MessageBase):
    id: int
    sender_id: int
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    title: str
    message: str
    type: str # contract, session, message, system
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    
class NotificationOut(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
