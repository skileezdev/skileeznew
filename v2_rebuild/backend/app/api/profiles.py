from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

from ..models.database import get_db
from ..models.user import User, CoachProfile, StudentProfile, Experience, Education, PortfolioItem, Language, StudentLanguage
from ..schemas.user import ExperienceBase, EducationBase, PortfolioItemBase, LanguageBase, StudentLanguageBase
from .deps import get_current_user

router = APIRouter(prefix="/profiles", tags=["Profiles"])

class ProfileUpdate(BaseModel):
    # Common
    bio: Optional[str] = None
    country: Optional[str] = None
    profile_picture: Optional[str] = None
    onboarding_completed: Optional[bool] = None
    profile_completion_percentage: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    # Coach Specific
    coach_title: Optional[str] = None
    goal: Optional[str] = None
    skills: Optional[str] = None
    hourly_rate: Optional[float] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    stripe_account_id: Optional[str] = None
    onboarding_step: Optional[int] = None
    
    # Coach Lists (Replace All strategy)
    experience: Optional[List[ExperienceBase]] = None
    education: Optional[List[EducationBase]] = None
    portfolio_items: Optional[List[PortfolioItemBase]] = None
    languages: Optional[List[LanguageBase]] = None

    # Student Specific
    age: Optional[int] = None
    preferred_languages: Optional[str] = None
    student_languages: Optional[List[StudentLanguageBase]] = None

@router.get("/me")
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's full profile including nested relationships"""
    # Force reload with joined relationships
    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(
            selectinload(User.coach_profile).selectinload(CoachProfile.experience),
            selectinload(User.coach_profile).selectinload(CoachProfile.education),
            selectinload(User.coach_profile).selectinload(CoachProfile.portfolio_items),
            selectinload(User.coach_profile).selectinload(CoachProfile.languages),
            selectinload(User.student_profile).selectinload(StudentProfile.languages)
        )
    )
    user = result.scalars().first()
    return user

@router.get("/{user_id}")
async def get_user_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get any user's public profile"""
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.coach_profile).selectinload(CoachProfile.experience),
            selectinload(User.coach_profile).selectinload(CoachProfile.education),
            selectinload(User.coach_profile).selectinload(CoachProfile.portfolio_items),
            selectinload(User.coach_profile).selectinload(CoachProfile.languages),
            selectinload(User.student_profile).selectinload(StudentProfile.languages)
        )
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user

@router.patch("/me")
async def update_my_profile(
    updates: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile with comprehensive V1 support"""
    
    # 1. Update User-level fields
    if updates.first_name is not None:
        current_user.first_name = updates.first_name
    if updates.last_name is not None:
        current_user.last_name = updates.last_name
    if updates.onboarding_completed is not None:
        current_user.onboarding_completed = updates.onboarding_completed
    if updates.profile_completion_percentage is not None:
        current_user.profile_completion_percentage = updates.profile_completion_percentage
    
    # 2. Update Role-Specific Profiles
    if current_user.current_role == "coach":
        if not current_user.coach_profile:
            # Auto-create if missing (shouldn't happen for signed up coaches usually)
            current_user.coach_profile = CoachProfile(user_id=current_user.id)
            db.add(current_user.coach_profile)
            await db.flush() # Get ID
        
        profile = current_user.coach_profile
        
        # Scalar Fields
        if updates.coach_title is not None: profile.coach_title = updates.coach_title
        if updates.bio is not None: profile.bio = updates.bio
        if updates.goal is not None: profile.goal = updates.goal
        if updates.skills is not None: profile.skills = updates.skills
        if updates.hourly_rate is not None: profile.hourly_rate = updates.hourly_rate
        if updates.country is not None: profile.country = updates.country
        if updates.phone_number is not None: profile.phone_number = updates.phone_number
        if updates.date_of_birth is not None: profile.date_of_birth = updates.date_of_birth
        if updates.stripe_account_id is not None: profile.stripe_account_id = updates.stripe_account_id
        if updates.onboarding_step is not None: profile.onboarding_step = updates.onboarding_step
        if updates.profile_picture is not None: profile.profile_picture = updates.profile_picture

        # List Fields (Replace All Strategy)
        if updates.experience is not None:
            # Delete existing
            await db.execute(select(Experience).where(Experience.coach_profile_id == profile.id)) # Just fetch? No, DELETE.
            # SQLAlchemy async delete is ... db.execute(delete(Experience)...)
            # Safe way: iterate and delete, or bulk delete.
            # Using basic relationship clear if possible, but simpler to use explicit DB commands for control
            # Actually, `profile.experience = []` works well with cascade, but we need to be careful with async.
            # Let's use direct delete queries for efficiency.
            from sqlalchemy import delete
            await db.execute(delete(Experience).where(Experience.coach_profile_id == profile.id))
            
            # Add new
            for exp_data in updates.experience:
                new_exp = Experience(**exp_data.model_dump(), coach_profile_id=profile.id)
                db.add(new_exp)

        if updates.education is not None:
            from sqlalchemy import delete
            await db.execute(delete(Education).where(Education.coach_profile_id == profile.id))
            for edu_data in updates.education:
                new_edu = Education(**edu_data.model_dump(), coach_profile_id=profile.id)
                db.add(new_edu)

        if updates.portfolio_items is not None:
            from sqlalchemy import delete
            await db.execute(delete(PortfolioItem).where(PortfolioItem.coach_profile_id == profile.id))
            for port_data in updates.portfolio_items:
                new_port = PortfolioItem(**port_data.model_dump(), coach_profile_id=profile.id)
                db.add(new_port)

        if updates.languages is not None:
            from sqlalchemy import delete
            await db.execute(delete(Language).where(Language.coach_profile_id == profile.id))
            for lang_data in updates.languages:
                new_lang = Language(**lang_data.model_dump(), coach_profile_id=profile.id)
                db.add(new_lang)
            
    elif current_user.current_role == "student":
        if not current_user.student_profile:
             current_user.student_profile = StudentProfile(user_id=current_user.id)
             db.add(current_user.student_profile)
             await db.flush()
        
        profile = current_user.student_profile
        
        # Scalar Fields
        if updates.bio is not None: profile.bio = updates.bio
        if updates.country is not None: profile.country = updates.country
        if updates.age is not None: profile.age = updates.age
        if updates.preferred_languages is not None: profile.preferred_languages = updates.preferred_languages
        if updates.profile_picture is not None: profile.profile_picture = updates.profile_picture
        
        # List Fields
        if updates.student_languages is not None:
            from sqlalchemy import delete
            await db.execute(delete(StudentLanguage).where(StudentLanguage.student_profile_id == profile.id))
            for lang_data in updates.student_languages:
                new_lang = StudentLanguage(**lang_data.model_dump(), student_profile_id=profile.id)
                db.add(new_lang)
    
    await db.commit()
    return {"message": "Profile updated successfully"}
