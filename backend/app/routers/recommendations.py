from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.recommendation import RecommendationResponse
from app.services import recommendation_service

router = APIRouter(prefix="/recommendations", tags=["recommendations"])
limiter = Limiter(key_func=get_remote_address)


@router.get("", response_model=Optional[RecommendationResponse])
@limiter.limit("10/minute")
async def get_recommendation(
    request: Request,
    lat: float = Query(...),
    lng: float = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await recommendation_service.get_recommendation(db, current_user, lat, lng)
