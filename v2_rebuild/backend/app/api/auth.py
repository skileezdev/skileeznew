from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserOut, Token
from ..services.auth import create_user, authenticate_user, switch_user_role
from ..core.security import create_access_token
from .deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserOut)
async def signup(
    user_in: UserCreate, 
    initial_role: str = Query("student", enum=["student", "coach"]),
    db: AsyncSession = Depends(get_db)
):
    return await create_user(db, user_in, initial_role=initial_role)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/switch-role", response_model=UserOut)
async def switch_role(
    target_role: str = Query(..., enum=["student", "coach"]),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await switch_user_role(db, current_user, target_role)
