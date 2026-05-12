import json
from math import cos, radians
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.food_truck import FoodTruck
from app.models.menu import Menu
from app.models.review import Review
from app.models.user import User
from app.schemas.truck import (
    TruckListItem, TruckDetail, TruckCreateResponse,
    LocationUpdateResponse, StatusUpdateResponse,
    MenuSchema, OwnerBrief, KeywordsResponse, NearestTruckResponse,
)
from app.services.ai_service import generate_keywords


async def _save_keywords(db: AsyncSession, truck_id: int) -> None:
    """키워드 생성 후 DB 저장. 실패해도 예외를 삼켜 트럭 등록에 영향 없음."""
    if not settings.GEMINI_API_KEY:
        return
    try:
        result = await db.execute(
            select(FoodTruck)
            .options(selectinload(FoodTruck.menus), selectinload(FoodTruck.reviews))
            .where(FoodTruck.id == truck_id)
        )
        truck = result.scalar_one_or_none()
        if not truck:
            return
        menu_names = [m.name for m in truck.menus]
        review_contents = [r.content for r in truck.reviews]
        keywords = await generate_keywords(truck.name, truck.description, menu_names, review_contents)
        truck.keywords = json.dumps(keywords, ensure_ascii=False)
        await db.commit()
    except Exception:
        pass


def _to_list_item(truck: FoodTruck) -> TruckListItem:
    menus = [MenuSchema.model_validate(m) for m in truck.menus]
    rep = menus[0].name if menus else None
    return TruckListItem(
        id=truck.id,
        name=truck.name,
        description=truck.description,
        latitude=truck.latitude,
        longitude=truck.longitude,
        is_open=truck.is_open,
        avg_rating=float(truck.avg_rating or 0),
        review_count=truck.review_count or 0,
        account_info=truck.account_info,
        representative_menu=rep,
        image_url=truck.image_url,
        menus=menus,
    )


def _to_detail(truck: FoodTruck) -> TruckDetail:
    menus = [MenuSchema.model_validate(m) for m in truck.menus]
    owner = OwnerBrief.model_validate(truck.owner) if truck.owner else None
    return TruckDetail(
        id=truck.id,
        name=truck.name,
        description=truck.description,
        latitude=truck.latitude,
        longitude=truck.longitude,
        is_open=truck.is_open,
        avg_rating=float(truck.avg_rating or 0),
        review_count=truck.review_count or 0,
        account_info=truck.account_info,
        image_url=truck.image_url,
        menus=menus,
        owner=owner,
    )


async def get_trucks(db: AsyncSession, lat: float, lng: float, radius: int = 2000) -> list[TruckListItem]:
    lat_delta = radius / 111_000
    lng_delta = radius / (111_000 * abs(cos(radians(lat))) + 0.0001)
    result = await db.execute(
        select(FoodTruck)
        .options(selectinload(FoodTruck.menus))
        .where(
            FoodTruck.is_open == True,
            FoodTruck.latitude.between(lat - lat_delta, lat + lat_delta),
            FoodTruck.longitude.between(lng - lng_delta, lng + lng_delta),
        )
    )
    trucks = result.scalars().all()
    return [_to_list_item(t) for t in trucks]


async def get_truck(db: AsyncSession, truck_id: int) -> TruckDetail:
    result = await db.execute(
        select(FoodTruck)
        .options(selectinload(FoodTruck.menus), selectinload(FoodTruck.owner))
        .where(FoodTruck.id == truck_id)
    )
    truck = result.scalar_one_or_none()
    if not truck:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")
    return _to_detail(truck)


async def get_my_truck(db: AsyncSession, owner: User) -> TruckDetail:
    result = await db.execute(
        select(FoodTruck)
        .options(selectinload(FoodTruck.menus), selectinload(FoodTruck.owner))
        .where(FoodTruck.owner_id == owner.id)
    )
    truck = result.scalar_one_or_none()
    if not truck:
        raise HTTPException(status_code=404, detail="등록된 가게가 없습니다.")
    return _to_detail(truck)


async def create_truck(
    db: AsyncSession,
    owner: User,
    name: str,
    menus_data: list[dict],
    latitude: float,
    longitude: float,
    description: Optional[str],
    account_info: Optional[str],
) -> TruckCreateResponse:
    existing = await db.execute(select(FoodTruck).where(FoodTruck.owner_id == owner.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="이미 등록된 가게가 있습니다.")

    truck = FoodTruck(
        owner_id=owner.id,
        name=name,
        description=description,
        latitude=latitude,
        longitude=longitude,
        account_info=account_info,
    )
    db.add(truck)
    await db.flush()

    for m in menus_data:
        db.add(Menu(truck_id=truck.id, name=m["name"], price=int(m["price"])))

    await db.commit()
    await db.refresh(truck)
    await _save_keywords(db, truck.id)
    return TruckCreateResponse.model_validate(truck)


async def update_menus(db: AsyncSession, truck_id: int, owner: User, menus_data: list[dict]) -> KeywordsResponse:
    result = await db.execute(select(FoodTruck).where(FoodTruck.id == truck_id, FoodTruck.owner_id == owner.id))
    truck = result.scalar_one_or_none()
    if not truck:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")

    await db.execute(delete(Menu).where(Menu.truck_id == truck_id))
    for m in menus_data:
        db.add(Menu(truck_id=truck_id, name=m["name"], price=int(m["price"])))

    truck.keywords = None
    await db.commit()
    await _save_keywords(db, truck_id)

    result2 = await db.execute(select(FoodTruck).where(FoodTruck.id == truck_id))
    updated = result2.scalar_one_or_none()
    if updated and updated.keywords:
        return KeywordsResponse(keywords=json.loads(updated.keywords))
    return KeywordsResponse(keywords=[])


async def update_location(db: AsyncSession, truck_id: int, owner: User, latitude: float, longitude: float) -> LocationUpdateResponse:
    result = await db.execute(select(FoodTruck).where(FoodTruck.id == truck_id, FoodTruck.owner_id == owner.id))
    truck = result.scalar_one_or_none()
    if not truck:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")
    truck.latitude = latitude
    truck.longitude = longitude
    await db.commit()
    await db.refresh(truck)
    return LocationUpdateResponse(id=truck.id, latitude=truck.latitude, longitude=truck.longitude)


async def update_status(db: AsyncSession, truck_id: int, owner: User, is_open: bool) -> StatusUpdateResponse:
    result = await db.execute(select(FoodTruck).where(FoodTruck.id == truck_id, FoodTruck.owner_id == owner.id))
    truck = result.scalar_one_or_none()
    if not truck:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")
    truck.is_open = is_open
    await db.commit()
    await db.refresh(truck)
    return StatusUpdateResponse(id=truck.id, is_open=truck.is_open)


async def get_or_generate_keywords(db: AsyncSession, truck_id: int) -> KeywordsResponse:
    result = await db.execute(select(FoodTruck).where(FoodTruck.id == truck_id))
    truck = result.scalar_one_or_none()
    if not truck:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")

    if truck.keywords:
        return KeywordsResponse(keywords=json.loads(truck.keywords))
    return KeywordsResponse(keywords=[])


async def get_nearest_truck(db: AsyncSession, lat: float, lng: float) -> NearestTruckResponse:
    result = await db.execute(select(FoodTruck).where(FoodTruck.is_open == True))
    trucks = result.scalars().all()
    if not trucks:
        return NearestTruckResponse()

    def dist_sq(t: FoodTruck) -> float:
        dlat = t.latitude - lat
        dlng = (t.longitude - lng) * cos(radians((t.latitude + lat) / 2))
        return dlat * dlat + dlng * dlng

    nearest = min(trucks, key=dist_sq)
    return NearestTruckResponse(latitude=nearest.latitude, longitude=nearest.longitude)
