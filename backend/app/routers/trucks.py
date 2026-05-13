from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user, require_owner
from app.models.user import User
from app.schemas.truck import (
    TruckListItem, TruckDetail, TruckCreateResponse, TruckCreate,
    LocationUpdate, StatusUpdate, LocationUpdateResponse, StatusUpdateResponse,
    KeywordsResponse, NearestTruckResponse, MenusUpdate,
)
from app.services import truck_service, ai_service

router = APIRouter(prefix="/trucks", tags=["trucks"])


@router.get("", response_model=list[TruckListItem])
async def list_trucks(
    lat: float = Query(...),
    lng: float = Query(...),
    radius: int = Query(2000),
    db: AsyncSession = Depends(get_db),
):
    return await truck_service.get_trucks(db, lat, lng, radius)


@router.get("/nearest", response_model=NearestTruckResponse)
async def get_nearest_truck(
    lat: float = Query(...),
    lng: float = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await truck_service.get_nearest_truck(db, lat, lng)


@router.get("/my", response_model=TruckDetail)
async def my_truck(
    current_user: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    return await truck_service.get_my_truck(db, current_user)


@router.get("/{truck_id}/keywords", response_model=KeywordsResponse)
async def get_keywords(truck_id: int, db: AsyncSession = Depends(get_db)):
    return await truck_service.get_or_generate_keywords(db, truck_id)


@router.get("/{truck_id}", response_model=TruckDetail)
async def get_truck(truck_id: int, db: AsyncSession = Depends(get_db)):
    return await truck_service.get_truck(db, truck_id)


@router.post("", response_model=TruckCreateResponse, status_code=201)
async def create_truck(
    data: TruckCreate,
    current_user: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    return await truck_service.create_truck(
        db, current_user, data.name, [m.model_dump() for m in data.menus],
        data.latitude, data.longitude, data.description, data.account_info
    )


@router.delete("/my", status_code=204)
async def delete_my_truck(
    current_user: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    await truck_service.delete_truck(db, current_user)


@router.patch("/{truck_id}/menus", response_model=KeywordsResponse)
async def update_menus(
    truck_id: int,
    data: MenusUpdate,
    current_user: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    return await truck_service.update_menus(db, truck_id, current_user, [m.model_dump() for m in data.menus])


@router.patch("/{truck_id}/location", response_model=LocationUpdateResponse)
async def update_location(
    truck_id: int,
    data: LocationUpdate,
    current_user: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    return await truck_service.update_location(db, truck_id, current_user, data.latitude, data.longitude)


@router.patch("/{truck_id}/status", response_model=StatusUpdateResponse)
async def update_status(
    truck_id: int,
    data: StatusUpdate,
    current_user: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    return await truck_service.update_status(db, truck_id, current_user, data.is_open)
