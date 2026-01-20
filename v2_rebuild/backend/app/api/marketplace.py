from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, timezone

from ..models.database import get_db
from ..models.marketplace import LearningRequest, Proposal, Contract, Session, ScreeningQuestion, ScreeningAnswer
from ..models.user import User, CoachProfile
from ..schemas.marketplace import (
    LearningRequestCreate, 
    LearningRequestOut, 
    ProposalCreate, 
    ProposalOut,
    ContractOut,
    SessionOut,
    CoachProfileOut
)
from .deps import get_current_user

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

@router.get("/coaches", response_model=List[CoachProfileOut])
async def get_coaches(
    search: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    sort: str = "top",
    db: AsyncSession = Depends(get_db)
):
    """Discovery endpoint for coaches (V1 1:1 Parity)"""
    query = select(CoachProfile).where(CoachProfile.is_approved == True).options(
        selectinload(CoachProfile.user),
        selectinload(CoachProfile.experience)
    )
    
    if search:
        search_term = f"%{search}%"
        # Join with User for search parity
        query = query.join(User).filter(
            (CoachProfile.coach_title.ilike(search_term)) |
            (CoachProfile.bio.ilike(search_term)) |
            (User.first_name.ilike(search_term)) |
            (User.last_name.ilike(search_term))
        )
        
    if price_min is not None:
        query = query.where(CoachProfile.hourly_rate >= price_min)
    if price_max is not None:
        query = query.where(CoachProfile.hourly_rate <= price_max)
        
    # Sorting
    if sort == 'rating':
        query = query.order_by(CoachProfile.rating.desc())
    elif sort == 'price_low':
        query = query.order_by(CoachProfile.hourly_rate.asc())
    elif sort == 'price_high':
        query = query.order_by(CoachProfile.hourly_rate.desc())
    else: # Default 'top'
        query = query.order_by(CoachProfile.rating.desc(), CoachProfile.hourly_rate.asc())

    result = await db.execute(query)
    return result.scalars().all()

@router.get("/requests", response_model=List[LearningRequestOut])
async def get_all_requests(db: AsyncSession = Depends(get_db)):
    """List all active learning requests"""
    result = await db.execute(
        select(LearningRequest)
        .where(LearningRequest.is_active == True)
        .options(
            selectinload(LearningRequest.student),
            selectinload(LearningRequest.screening_questions)
        )
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
    data = request_in.model_dump()
    screening_questions_data = data.pop("screening_questions", [])
    
    new_request = LearningRequest(
        **data,
        student_id=current_user.id
    )
    db.add(new_request)
    await db.flush() # Get ID for questions
    
    for idx, q_data in enumerate(screening_questions_data):
        q = ScreeningQuestion(
            learning_request_id=new_request.id,
            question_text=q_data["question_text"],
            order_index=q_data.get("order_index", idx)
        )
        db.add(q)
        
    await db.commit()
    await db.refresh(new_request)
    
    # Refresh to load relationships
    result = await db.execute(
        select(LearningRequest)
        .where(LearningRequest.id == new_request.id)
        .options(
            selectinload(LearningRequest.student),
            selectinload(LearningRequest.screening_questions)
        )
    )
    return result.scalar_one()

@router.post("/proposals", response_model=ProposalOut)
async def submit_proposal(
    proposal_in: ProposalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit a proposal for a learning request (Coach only)"""
    # 1:1 Mirror Logic - Validate request
    result = await db.execute(
        select(LearningRequest)
        .where(LearningRequest.id == proposal_in.learning_request_id)
        .options(selectinload(LearningRequest.screening_questions))
    )
    learning_request = result.scalars().first()
    if not learning_request:
        raise HTTPException(status_code=404, detail="Learning request not found")

    data = proposal_in.model_dump()
    answers_data = data.pop("answers", [])
    
    # Store answers in JSON fields (V1 parity) + direct relationships (V2 best practice)
    new_proposal = Proposal(
        **data,
        coach_id=current_user.id,
        answers=[a for a in answers_data] # Keep JSON parity
    )
    db.add(new_proposal)
    await db.flush()
    
    for a_data in answers_data:
        ans = ScreeningAnswer(
            proposal_id=new_proposal.id,
            question_id=a_data["question_id"],
            answer_text=a_data["answer_text"]
        )
        db.add(ans)
        
    await db.commit()
    await db.refresh(new_proposal)
    return new_proposal

async def _generate_contract_number(db: AsyncSession):
    # Mirroring V1 format: #001
    result = await db.execute(
        select(Contract).order_by(Contract.id.desc()).limit(1)
    )
    last_contract = result.scalars().first()
    if not last_contract:
        return "#001"
    
    try:
        last_num = int(last_contract.contract_number.replace("#", ""))
    except (ValueError, AttributeError):
        last_num = 0
        
    return f"#{last_num + 1:03d}"

@router.post("/proposals/{proposal_id}/accept", response_model=ContractOut)
async def accept_proposal(
    proposal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept a coach's proposal and create a contract (Student only)"""
    result = await db.execute(
        select(Proposal)
        .where(Proposal.id == proposal_id)
        .options(selectinload(Proposal.learning_request))
    )
    proposal = result.scalars().first()
    
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    if proposal.learning_request.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    if proposal.status != 'pending':
        raise HTTPException(status_code=400, detail="Proposal already processed")

    # 1. Update status
    proposal.status = 'accepted'
    proposal.learning_request.is_active = False 
    
    # 2. Create Contract (Mirrored V1 fields)
    contract_number = await _generate_contract_number(db)
    new_contract = Contract(
        proposal_id=proposal.id,
        student_id=current_user.id,
        coach_id=proposal.coach_id,
        contract_number=contract_number,
        total_amount=proposal.price_per_session * proposal.session_count,
        total_sessions=proposal.session_count,
        rate=proposal.price_per_session,
        payment_model="per_session",
        status="awaiting_response" # V1 logic: awaiting_response -> payment -> active
    )
    db.add(new_contract)
    await db.flush() 
    
    # 3. Create Session placeholders (V1 mirrored logic)
    for i in range(proposal.session_count):
        session = Session(
            contract_id=new_contract.id,
            session_number=i + 1,
            status="scheduled",
            duration_minutes=60 # Default
        )
        db.add(session)
    
    await db.commit()
    await db.refresh(new_contract)
    return new_contract
