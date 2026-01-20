from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from ..models.database import get_db
from ..models.user import User, StudentProfile, CoachProfile, Experience, Education, PortfolioItem
from ..schemas.user import UserOut # Assuming this exists or we can use a generic one
from .deps import get_current_user

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.get("/me", response_model=None) # We'll return a rich object
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the full rich profile for the current user (1:1 Mirror)"""
    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(
            selectinload(User.student_profile),
            selectinload(User.coach_profile).selectinload(CoachProfile.experience),
            selectinload(User.coach_profile).selectinload(CoachProfile.education),
            selectinload(User.coach_profile).selectinload(CoachProfile.portfolio_items)
        )
    )
    user = result.scalars().first()
    return user

@router.post("/update")
async def update_profile(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update profile fields (V1 Parity)"""
    # Logic to update user, student_profile, or coach_profile
    if "first_name" in data: current_user.first_name = data["first_name"]
    if "last_name" in data: current_user.last_name = data["last_name"]
    
    if current_user.current_role == 'student' and current_user.student_profile:
        if "bio" in data: current_user.student_profile.bio = data["bio"]
        if "interests" in data: current_user.student_profile.interests = data["interests"]
        
    elif current_user.current_role == 'coach' and current_user.coach_profile:
        if "coach_title" in data: current_user.coach_profile.coach_title = data["coach_title"]
        if "bio" in data: current_user.coach_profile.bio = data["bio"]
        if "hourly_rate" in data: current_user.coach_profile.hourly_rate = data["hourly_rate"]
        
    await db.commit()
    return {"message": "Profile updated"}

@router.post("/experience")
async def add_experience(
    exp_in: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.coach_profile:
        raise HTTPException(status_code=400, detail="Coach profile required")
        
    new_exp = Experience(
        coach_profile_id=current_user.coach_profile.id,
        title=exp_in["title"],
        company=exp_in["company"],
        start_date=exp_in["start_date"], # Should handle date parsing in real app
        end_date=exp_in.get("end_date"),
        is_current=exp_in.get("is_current", False),
        description=exp_in.get("description")
    )
    db.add(new_exp)
    await db.commit()
    return {"message": "Experience added"}

@router.delete("/experience/{exp_id}")
async def delete_experience(
    exp_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Experience).where(Experience.id == exp_id))
    exp = result.scalars().first()
    if exp and exp.coach_profile_id == current_user.coach_profile.id:
        await db.delete(exp)
        await db.commit()
    return {"message": "Experience deleted"}
