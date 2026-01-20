from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from ..models.database import get_db
from ..models.marketplace import LearningRequest, Proposal
from ..schemas.marketplace import (
    LearningRequestCreate, 
    LearningRequestOut, 
    ProposalCreate, 
    ProposalOut,
    ContractOut,
    SessionOut
)
from ..models.user import User
from .deps import get_current_user

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

@router.get("/requests", response_model=List[LearningRequestOut])
async def get_all_requests(db: AsyncSession = Depends(get_db)):
    """List all active learning requests"""
    result = await db.execute(
        select(LearningRequest)
        .where(LearningRequest.is_active == True)
        .options(selectinload(LearningRequest.student))
        .order_by(LearningRequest.created_at.desc())
    )
    return result.scalars().all()

@router.post("/requests", response_model=LearningRequestOut)
async def create_request(
    request_in: LearningRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new learning request (Student only)"""
    new_request = LearningRequest(
        **request_in.model_dump(),
        student_id=current_user.id
    )
    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)
    # Refresh to load student relationship
    result = await db.execute(
        select(LearningRequest)
        .where(LearningRequest.id == new_request.id)
        .options(selectinload(LearningRequest.student))
    )
    return result.scalar_one()

@router.post("/proposals", response_model=ProposalOut)
async def submit_proposal(
    proposal_in: ProposalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit a proposal for a learning request (Coach only)"""
    # Check if request exists
    request_result = await db.execute(
        select(LearningRequest).where(LearningRequest.id == proposal_in.learning_request_id)
    )
    learning_request = request_result.scalars().first()
    if not learning_request:
        raise HTTPException(status_code=404, detail="Learning request not found")

    new_proposal = Proposal(
        **proposal_in.model_dump(),
        coach_id=current_user.id
    )
    db.add(new_proposal)
    await db.commit()
    await db.refresh(new_proposal)
    
from ..models.marketplace import LearningRequest, Proposal, Contract, Session

@router.post("/proposals/{proposal_id}/accept", response_model=ContractOut)
async def accept_proposal(
    proposal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept a coach's proposal and create a contract (Student only)"""
    # Load proposal with its learning request
    result = await db.execute(
        select(Proposal)
        .where(Proposal.id == proposal_id)
        .options(selectinload(Proposal.learning_request))
    )
    proposal = result.scalars().first()
    
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    if proposal.learning_request.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the student who created the request can accept proposals")
    
    if proposal.status != 'pending':
        raise HTTPException(status_code=400, detail="Proposal already processed")

    # 1. Update status
    proposal.status = 'accepted'
    proposal.learning_request.is_active = False # Close the original request
    
    # 2. Create Contract
    new_contract = Contract(
        proposal_id=proposal.id,
        student_id=current_user.id,
        coach_id=proposal.coach_id,
        total_amount=proposal.price_per_session * proposal.session_count,
        status="active"
    )
    db.add(new_contract)
    await db.flush() # Get contract ID
    
    # 3. Create Session placeholders
    for i in range(proposal.session_count):
        session = Session(
            contract_id=new_contract.id,
            session_number=i + 1,
            status="scheduled"
        )
        db.add(session)
    
    await db.commit()
    await db.refresh(new_contract)
    
    return new_contract
