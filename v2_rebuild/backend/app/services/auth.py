from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime, timezone
from ..models.user import User, RoleSwitchLog, StudentProfile, CoachProfile
from ..schemas.user import UserCreate
from ..core.security import get_password_hash, verify_password, create_access_token

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.student_profile),
            selectinload(User.coach_profile).options(
                selectinload(CoachProfile.experience),
                selectinload(CoachProfile.education),
                selectinload(CoachProfile.portfolio_items)
            )
        )
        .where(User.email == email)
    )
    return result.scalars().first()

async def create_user(db: AsyncSession, user_in: UserCreate, initial_role: str = "student"):
    db_user = await get_user_by_email(db, user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        password_hash=hashed_password,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        is_student=(initial_role == "student"),
        is_coach=(initial_role == "coach"),
        current_role=initial_role
    )
    
    db.add(new_user)
    await db.flush() # Get ID before profiles
    
    if initial_role == "student":
        db.add(StudentProfile(user_id=new_user.id))
    elif initial_role == "coach":
        db.add(CoachProfile(user_id=new_user.id))
        
    # Capture ID before commit expires the object
    new_user_id = new_user.id
        
    await db.commit()
    
    # Re-fetch with eager loading to avoid MissingGreenlet error
    # Use the captured ID instead of accessing the expired object
    result = await db.execute(
        select(User)
        .options(selectinload(User.student_profile), selectinload(User.coach_profile))
        .where(User.id == new_user_id)
    )
    return result.scalars().first()

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalars().first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

async def switch_user_role(db: AsyncSession, user: User, target_role: str):
    if target_role not in ["student", "coach"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # 1:1 Mirror Logic
    from_role = user.current_role
    
    if target_role == "student" and not user.is_student:
        user.is_student = True
        db.add(StudentProfile(user_id=user.id))
    elif target_role == "coach" and not user.is_coach:
        user.is_coach = True
        db.add(CoachProfile(user_id=user.id))
        
    user.current_role = target_role
    user.last_role_switch = datetime.now(timezone.utc)
    user.role_switch_count += 1
    
    log = RoleSwitchLog(
        user_id=user.id,
        from_role=from_role,
        to_role=target_role,
        switch_reason="User manual switch"
    )
    db.add(log)
    
    # Capture ID before commit
    user_id = user.id
    
    await db.commit()
    
    # Re-fetch with eager loading
    result = await db.execute(
        select(User)
        .options(selectinload(User.student_profile), selectinload(User.coach_profile))
        .where(User.id == user_id)
    )
    return result.scalars().first()
