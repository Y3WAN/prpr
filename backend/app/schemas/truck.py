from pydantic import BaseModel, Field
from typing import Optional
import json


class MenuSchema(BaseModel):
    id: Optional[int] = None
    name: str
    price: int

    model_config = {"from_attributes": True}


class OwnerBrief(BaseModel):
    id: int
    nickname: str

    model_config = {"from_attributes": True}


class TruckListItem(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    is_open: bool
    avg_rating: float
    review_count: int
    account_info: Optional[str] = None
    representative_menu: Optional[str] = None
    image_url: Optional[str] = None
    menus: list[MenuSchema] = []

    model_config = {"from_attributes": True}


class TruckDetail(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    is_open: bool
    avg_rating: float
    review_count: int
    account_info: Optional[str] = None
    image_url: Optional[str] = None
    menus: list[MenuSchema] = []
    owner: Optional[OwnerBrief] = None

    model_config = {"from_attributes": True}


class TruckCreateResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    is_open: bool

    model_config = {"from_attributes": True}


class LocationUpdate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class StatusUpdate(BaseModel):
    is_open: bool


class LocationUpdateResponse(BaseModel):
    id: int
    latitude: float
    longitude: float

    model_config = {"from_attributes": True}


class StatusUpdateResponse(BaseModel):
    id: int
    is_open: bool

    model_config = {"from_attributes": True}


class KeywordsResponse(BaseModel):
    keywords: list[str]


class NearestTruckResponse(BaseModel):
    latitude: float | None = None
    longitude: float | None = None


class MenusUpdate(BaseModel):
    menus: list[MenuSchema]


class TruckCreate(BaseModel):
    name: str
    menus: list[MenuSchema]
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    description: Optional[str] = None
    account_info: Optional[str] = None
