from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, and_, desc
from typing import List
from datetime import datetime, timezone

from ..models.database import get_db
from ..models.messaging import Message, Notification
from ..models.user import User
from ..models.marketplace import Contract, Proposal, LearningRequest
from ..schemas.messaging import MessageCreate, MessageOut, NotificationOut
from .deps import get_current_user

router = APIRouter(prefix="/messages", tags=["Messaging"])

@router.get("/", response_model=List[MessageOut])
async def get_messages(
    other_user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get conversation history with another user"""
    # 1:1 Parity: Fetch filtered by sender/recipient pair
    result = await db.execute(
        select(Message)
        .where(
            or_(
                (Message.sender_id == current_user.id) & (Message.recipient_id == other_user_id),
                (Message.sender_id == other_user_id) & (Message.recipient_id == current_user.id)
            )
        )
        .order_by(Message.created_at.asc())
    )
    return result.scalars().all()

@router.post("/", response_model=MessageOut)
async def send_message(
    msg_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message"""
    # Validate recipient
    result = await db.execute(select(User).where(User.id == msg_in.recipient_id))
    recipient = result.scalars().first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
        
    new_msg = Message(
        **msg_in.model_dump(),
        sender_id=current_user.id
    )
    db.add(new_msg)
    
    # Create notification for recipient
    notif = Notification(
        user_id=recipient.id,
        title=f"New message from {current_user.first_name}",
        message=f"{msg_in.content[:50]}...",
        type="message",
        related_id=current_user.id, # Link to sender for quick reply
        related_type="user"
    )
    db.add(notif)
    
    await db.commit()
    await db.refresh(new_msg)
    return new_msg

@router.get("/notifications", response_model=List[NotificationOut])
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user notifications"""
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    )
    return result.scalars().all()

@router.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of recent conversations (for sidebar)"""
    # This is a complex query to get distinct users.
    # For now, simplistic approach: Get all unique conversation partners.
    # Proper SQL would be better but keeping it simple for V2 prototype first.
    
    # Find all messages involving user
    result = await db.execute(
        select(Message)
        .where(or_(Message.sender_id == current_user.id, Message.recipient_id == current_user.id))
        .order_by(Message.created_at.desc())
    )
    messages = result.scalars().all()
    
    # Process in python
    partners = {}
    for m in messages:
        pid = m.recipient_id if m.sender_id == current_user.id else m.sender_id
        if pid not in partners:
            partners[pid] = {
                "user_id": pid,
                "last_message": m.content,
                "timestamp": m.created_at,
                "unread": 0 # Logic needed
            }
            
    return list(partners.values())

@router.get("/context/{other_user_id}")
async def get_conversation_context(
    other_user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the active context (Contract or Proposal) between two users"""
    # 1. Check for active contract
    contract_res = await db.execute(
        select(Contract)
        .where(
            or_(
                (Contract.student_id == current_user.id) & (Contract.coach_id == other_user_id),
                (Contract.student_id == other_user_id) & (Contract.coach_id == current_user.id)
            )
        )
        .order_by(Contract.created_at.desc())
    )
    contract = contract_res.scalars().first()
    if contract:
        return {
            "type": "contract",
            "id": contract.id,
            "status": contract.status,
            "title": f"Contract #{contract.contract_number}",
            "amount": float(contract.total_amount),
            "sessions": contract.total_sessions
        }
        
    # 2. Check for pending proposal
    proposal_res = await db.execute(
        select(Proposal)
        .join(LearningRequest)
        .where(
            or_(
                (Proposal.coach_id == current_user.id) & (LearningRequest.student_id == other_user_id),
                (Proposal.coach_id == other_user_id) & (LearningRequest.student_id == current_user.id)
            )
        )
        .order_by(Proposal.created_at.desc())
        .options(selectinload(Proposal.learning_request))
    )
    proposal = proposal_res.scalars().first()
    if proposal:
        return {
            "type": "proposal",
            "id": proposal.id,
            "status": proposal.status,
            "title": proposal.learning_request.title,
            "amount": proposal.price_per_session,
            "sessions": proposal.session_count
        }
        
    return None
