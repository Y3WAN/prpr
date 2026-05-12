from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import verify_jwt
from app.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    user = await db.get(User, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")
    return user


async def require_owner(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="푸드트럭 등록 권한이 없습니다.")
    return current_user


async def require_customer(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="사장님 계정은 리뷰를 작성할 수 없습니다.")
    return current_user
