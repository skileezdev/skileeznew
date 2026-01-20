from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional

from ..models.database import get_db
from ..models.user import User, CoachProfile, StudentProfile
from .deps import get_current_user

router = APIRouter(prefix="/profiles", tags=["Profiles"])

class ProfileUpdate(BaseModel):
    bio: Optional[str] = None
    coach_title: Optional[str] = None
    skills: Optional[str] = None
    hourly_rate: Optional[float] = None
    country: Optional[str] = None

@router.get("/me")
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's profile"""
    profile_data = {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "current_role": current_user.current_role
    }
    
    if current_user.current_role == "coach" and current_user.coach_profile:
        profile_data.update({
            "coach_title": current_user.coach_profile.coach_title,
            "bio": current_user.coach_profile.bio,
            "skills": current_user.coach_profile.skills,
            "hourly_rate": current_user.coach_profile.hourly_rate,
            "country": current_user.coach_profile.country,
            "rating": current_user.coach_profile.rating,
            "profile_picture": current_user.coach_profile.profile_picture
        })
    elif current_user.current_role == "student" and current_user.student_profile:
        profile_data.update({
            "bio": current_user.student_profile.bio,
            "country": current_user.student_profile.country,
            "profile_picture": current_user.student_profile.profile_picture
        })
    
    return profile_data

@router.patch("/me")
async def update_my_profile(
    updates: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile"""
    if current_user.current_role == "coach":
        if not current_user.coach_profile:
            raise HTTPException(status_code=404, detail="Coach profile not found")
        
        profile = current_user.coach_profile
        if updates.bio is not None:
            profile.bio = updates.bio
        if updates.coach_title is not None:
            profile.coach_title = updates.coach_title
        if updates.skills is not None:
            profile.skills = updates.skills
        if updates.hourly_rate is not None:
            profile.hourly_rate = updates.hourly_rate
        if updates.country is not None:
            profile.country = updates.country
            
    elif current_user.current_role == "student":
        if not current_user.student_profile:
            raise HTTPException(status_code=404, detail="Student profile not found")
        
        profile = current_user.student_profile
        if updates.bio is not None:
            profile.bio = updates.bio
        if updates.country is not None:
            profile.country = updates.country
    
    await db.commit()
    return {"message": "Profile updated successfully"}
