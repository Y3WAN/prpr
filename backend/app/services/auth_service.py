from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.user import User
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.schemas.auth import SignupRequest, LoginRequest, UserResponse, LoginResponse


async def signup(db: AsyncSession, data: SignupRequest) -> UserResponse:
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다.")

    user = User(
        email=data.email,
        password=hash_password(data.password),
        nickname=data.nickname,
        role=data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


async def login(db: AsyncSession, data: LoginRequest) -> LoginResponse:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    token = create_access_token(user.id)
    return LoginResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )
