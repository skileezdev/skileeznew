from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, timezone

from ..models.database import get_db
from ..models.marketplace import Contract, Session
from ..schemas.marketplace import ContractOut, SessionOut
from ..models.user import User
from .deps import get_current_user

router = APIRouter(prefix="/contracts", tags=["Contracts"])

@router.get("/sessions/all", response_model=List[SessionOut])
async def get_all_my_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all sessions for the current user across all contracts"""
    result = await db.execute(
        select(Session)
        .join(Contract)
        .where((Contract.student_id == current_user.id) | (Contract.coach_id == current_user.id))
        .order_by(Session.scheduled_at.asc())
    )
    return result.scalars().all()

@router.get("/sessions/{session_id}", response_model=SessionOut)
async def get_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed session information for the waiting room"""
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
        .options(
            selectinload(Session.proposal).selectinload(Proposal.contract).selectinload(Contract.student),
            selectinload(Session.proposal).selectinload(Proposal.contract).selectinload(Contract.coach)
        )
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Auth check
    if session.contract.student_id != current_user.id and session.contract.coach_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    return session

@router.get("", response_model=List[ContractOut])
async def get_my_contracts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Contract)
        .where((Contract.student_id == current_user.id) | (Contract.coach_id == current_user.id))
        .order_by(Contract.created_at.desc())
    )
    return result.scalars().all()

@router.get("/{contract_id}", response_model=ContractOut)
async def get_contract_detail(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed contract information with sessions (1:1 Mirror)"""
    result = await db.execute(
        select(Contract)
        .where(Contract.id == contract_id)
        .options(
            selectinload(Contract.sessions),
            selectinload(Contract.learning_request),
            selectinload(Contract.student),
            selectinload(Contract.coach)
        )
    )
    contract = result.scalars().first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    if contract.student_id != current_user.id and contract.coach_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    return contract

@router.get("/{contract_id}/sessions", response_model=List[SessionOut])
async def get_contract_sessions(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all sessions for a specific contract"""
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalars().first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    if contract.student_id != current_user.id and contract.coach_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    result = await db.execute(
        select(Session)
        .where(Session.proposal_id == contract.proposal_id)
        .order_by(Session.session_number.asc())
    )
    return result.scalars().all()

@router.post("/sessions/{session_id}/reschedule-request")
async def request_reschedule(
    session_id: int,
    new_date: datetime,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """1:1 Mirror: Request a session reschedule"""
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
        .options(selectinload(Session.proposal).selectinload(Proposal.contract))
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Auth
    if session.contract.student_id != current_user.id and session.contract.coach_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    session.reschedule_requested = True
    session.reschedule_requested_by = current_user.current_role
    session.reschedule_new_date = new_date
    session.reschedule_reason = reason
    
    await db.commit()
    return {"message": "Reschedule requested"}

@router.post("/sessions/{session_id}/reschedule-respond")
async def respond_reschedule(
    session_id: int,
    accept: bool,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """1:1 Mirror: Respond to a reschedule request"""
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
        .options(selectinload(Session.proposal).selectinload(Proposal.contract))
    )
    session = result.scalars().first()
    if not session or not session.reschedule_requested:
        raise HTTPException(status_code=404, detail="No active reschedule request")
    
    # Must be the OTHER person
    if session.reschedule_requested_by == current_user.current_role:
        raise HTTPException(status_code=400, detail="You cannot respond to your own request")

    if accept:
        session.scheduled_at = session.reschedule_new_date
        
    session.reschedule_requested = False
    session.reschedule_requested_by = None
    session.reschedule_new_date = None
    session.reschedule_reason = None
    
    await db.commit()
    return {"status": "accepted" if accept else "declined"}

@router.post("/sessions/{session_id}/start")
async def start_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """1:1 Mirror: Mark session as started"""
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
        .options(selectinload(Session.proposal).selectinload(Proposal.contract))
    )
    session = result.scalars().first()
    if not session or session.status != "scheduled":
        raise HTTPException(status_code=400, detail="Invalid session state")

    session.meeting_started_at = datetime.now(timezone.utc)
    session.status = "in_progress"
    await db.commit()
    return {"status": "in_progress"}

@router.post("/sessions/{session_id}/complete")
async def complete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """1:1 Mirror: Mark session as completed"""
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
        .options(selectinload(Session.proposal).selectinload(Proposal.contract))
    )
    session = result.scalars().first()
    if not session or session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Invalid session state")

    session.meeting_ended_at = datetime.now(timezone.utc)
    session.status = "completed"
    
    # Update contract progress
    session.contract.completed_sessions += 1
    if session.contract.completed_sessions >= session.contract.total_sessions:
        session.contract.status = "completed"
        
    await db.commit()
    return {"status": "completed"}
