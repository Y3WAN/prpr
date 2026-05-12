import json
from math import cos, radians, sqrt
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.food_truck import FoodTruck
from app.models.review import Review
from app.models.user import User
from app.schemas.recommendation import RecommendationResponse

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)


def _dist_m(lat1: float, lng1: float, lat2: float, lng2: float) -> int:
    dlat = (lat2 - lat1) * 111_000
    dlng = (lng2 - lng1) * 111_000 * cos(radians((lat1 + lat2) / 2))
    return int(sqrt(dlat * dlat + dlng * dlng))


def _fallback(candidates: list[FoodTruck], lat: float, lng: float) -> RecommendationResponse:
    t = candidates[0]
    food_type = t.menus[0].name[:4] if t.menus else "음식"
    return RecommendationResponse(
        truck_id=t.id,
        truck_name=t.name,
        food_type=food_type,
        distance_m=_dist_m(lat, lng, t.latitude, t.longitude),
        latitude=t.latitude,
        longitude=t.longitude,
    )


async def get_recommendation(
    db: AsyncSession, user: User, lat: float, lng: float
) -> Optional[RecommendationResponse]:
    # 사용자 리뷰 조회
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.truck).selectinload(FoodTruck.menus))
        .where(Review.user_id == user.id)
        .order_by(Review.created_at.desc())
        .limit(10)
    )
    reviews = result.scalars().all()
    if not reviews:
        return None

    # 영업중인 모든 트럭 조회 (위치 필터 없음 - 취향 기반 추천)
    result = await db.execute(
        select(FoodTruck)
        .options(selectinload(FoodTruck.menus))
        .where(FoodTruck.is_open == True)
    )
    all_trucks = result.scalars().all()

    # 이미 리뷰한 가게 제외
    reviewed_ids = {r.truck_id for r in reviews}
    candidates = [t for t in all_trucks if t.id not in reviewed_ids]
    if not candidates:
        return None

    if not settings.GEMINI_API_KEY:
        return _fallback(candidates, lat, lng)

    review_lines = "\n".join(
        f"- {r.truck.name}: {r.content} (별점 {r.rating}/5)" for r in reviews
    )
    candidate_lines = "\n".join(
        f"{i+1}. {t.name} - 메뉴: {', '.join(m.name for m in t.menus)}"
        for i, t in enumerate(candidates)
    )

    prompt = f"""사용자의 최근 리뷰 기록:
{review_lines}

현재 주변 가게들:
{candidate_lines}

사용자 취향에 가장 잘 맞는 가게 번호 하나를 골라줘.
반드시 아래 JSON 형식으로만 응답해 (다른 텍스트 없이):
{{"index": 번호, "food_type": "음식 종류 2~4글자"}}"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 60, "temperature": 0.3},
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                GEMINI_URL,
                params={"key": settings.GEMINI_API_KEY},
                json=payload,
            )
            resp.raise_for_status()

        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        start, end = text.find("{"), text.rfind("}") + 1
        data = json.loads(text[start:end])
        idx = int(data["index"]) - 1
        food_type = data.get("food_type", "")
        t = candidates[idx] if 0 <= idx < len(candidates) else candidates[0]

        return RecommendationResponse(
            truck_id=t.id,
            truck_name=t.name,
            food_type=food_type or (t.menus[0].name[:4] if t.menus else "음식"),
            distance_m=_dist_m(lat, lng, t.latitude, t.longitude),
            latitude=t.latitude,
            longitude=t.longitude,
        )
    except Exception:
        return _fallback(candidates, lat, lng)
