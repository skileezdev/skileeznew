from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from ..models.database import get_db
from ..models.marketplace import Contract, Session
from ..schemas.marketplace import ContractOut, SessionOut
from ..models.user import User
from .deps import get_current_user

router = APIRouter(prefix="/contracts", tags=["Contracts"])

@router.get("", response_model=List[ContractOut])
async def get_my_contracts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all active contracts for the current user (Student or Coach)"""
    result = await db.execute(
        select(Contract)
        .where((Contract.student_id == current_user.id) | (Contract.coach_id == current_user.id))
        .order_by(Contract.created_at.desc())
    )
    return result.scalars().all()

@router.get("/{contract_id}/sessions", response_model=List[SessionOut])
async def get_contract_sessions(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all sessions for a specific contract"""
    # Verify access
    contract_result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = contract_result.scalars().first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    if contract.student_id != current_user.id and contract.coach_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await db.execute(
        select(Session)
        .where(Session.contract_id == contract_id)
        .order_by(Session.session_number.asc())
    )
    return result.scalars().all()
