from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import SignupRequest, LoginRequest, UserResponse, LoginResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/signup", response_model=UserResponse, status_code=201)
@limiter.limit("10/minute")
async def signup(request: Request, data: SignupRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.signup(db, data)


@router.post("/login", response_model=LoginResponse)
@limiter.limit("20/minute")
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(db, data)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
