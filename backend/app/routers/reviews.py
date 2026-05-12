from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user, require_customer
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, MyReviewResponse
from app.services import review_service

router = APIRouter(tags=["reviews"])


@router.get("/trucks/{truck_id}/reviews", response_model=list[ReviewResponse])
async def get_reviews(truck_id: int, db: AsyncSession = Depends(get_db)):
    return await review_service.get_reviews(db, truck_id)


@router.post("/trucks/{truck_id}/reviews", response_model=ReviewResponse, status_code=201)
async def create_review(
    truck_id: int,
    data: ReviewCreate,
    current_user: User = Depends(require_customer),
    db: AsyncSession = Depends(get_db),
):
    return await review_service.create_review(db, truck_id, current_user, data)


@router.put("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await review_service.update_review(db, review_id, current_user, data)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await review_service.delete_review(db, review_id, current_user)


@router.get("/my/reviews", response_model=list[MyReviewResponse])
async def my_reviews(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await review_service.get_my_reviews(db, current_user)
