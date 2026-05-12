from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.review import Review
from app.models.food_truck import FoodTruck
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, MyReviewResponse, UserBrief, TruckBrief


async def recalculate_avg_rating(db: AsyncSession, truck_id: int):
    result = await db.execute(
        select(func.avg(Review.rating), func.count(Review.id))
        .where(Review.truck_id == truck_id)
    )
    avg, count = result.one()
    await db.execute(
        update(FoodTruck).where(FoodTruck.id == truck_id)
        .values(avg_rating=round(float(avg or 0), 2), review_count=count or 0)
    )


async def get_reviews(db: AsyncSession, truck_id: int) -> list[ReviewResponse]:
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.user))
        .where(Review.truck_id == truck_id)
        .order_by(Review.created_at.desc())
    )
    reviews = result.scalars().all()
    return [
        ReviewResponse(
            id=r.id,
            content=r.content,
            rating=r.rating,
            created_at=r.created_at,
            updated_at=r.updated_at,
            user=UserBrief.model_validate(r.user),
        )
        for r in reviews
    ]


async def create_review(db: AsyncSession, truck_id: int, user: User, data: ReviewCreate) -> ReviewResponse:
    truck = await db.get(FoodTruck, truck_id)
    if not truck:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")

    existing = await db.execute(
        select(Review).where(Review.truck_id == truck_id, Review.user_id == user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="이미 리뷰를 작성한 가게입니다.")

    review = Review(truck_id=truck_id, user_id=user.id, content=data.content, rating=data.rating)
    db.add(review)
    await db.flush()
    await recalculate_avg_rating(db, truck_id)
    await db.commit()
    await db.refresh(review)
    await db.refresh(user)

    return ReviewResponse(
        id=review.id,
        content=review.content,
        rating=review.rating,
        created_at=review.created_at,
        updated_at=review.updated_at,
        user=UserBrief.model_validate(user),
    )


async def update_review(db: AsyncSession, review_id: int, user: User, data: ReviewUpdate) -> ReviewResponse:
    result = await db.execute(
        select(Review).options(selectinload(Review.user)).where(Review.id == review_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")
    if review.user_id != user.id:
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

    review.content = data.content
    review.rating = data.rating
    await db.flush()
    await recalculate_avg_rating(db, review.truck_id)
    await db.commit()
    await db.refresh(review)

    return ReviewResponse(
        id=review.id,
        content=review.content,
        rating=review.rating,
        created_at=review.created_at,
        updated_at=review.updated_at,
        user=UserBrief.model_validate(review.user),
    )


async def delete_review(db: AsyncSession, review_id: int, user: User):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")
    if review.user_id != user.id:
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

    truck_id = review.truck_id
    await db.delete(review)
    await db.flush()
    await recalculate_avg_rating(db, truck_id)
    await db.commit()


async def get_my_reviews(db: AsyncSession, user: User) -> list[MyReviewResponse]:
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.truck))
        .where(Review.user_id == user.id)
        .order_by(Review.created_at.desc())
    )
    reviews = result.scalars().all()
    return [
        MyReviewResponse(
            id=r.id,
            content=r.content,
            rating=r.rating,
            truck=TruckBrief.model_validate(r.truck),
            created_at=r.created_at,
        )
        for r in reviews
    ]
