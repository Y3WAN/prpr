from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)
    rating: int = Field(..., ge=1, le=5)


class ReviewUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)
    rating: int = Field(..., ge=1, le=5)


class UserBrief(BaseModel):
    id: int
    nickname: str

    model_config = {"from_attributes": True}


class TruckBrief(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ReviewResponse(BaseModel):
    id: int
    content: str
    rating: int
    created_at: datetime
    updated_at: datetime
    user: UserBrief

    model_config = {"from_attributes": True}


class MyReviewResponse(BaseModel):
    id: int
    content: str
    rating: int
    truck: TruckBrief
    created_at: datetime

    model_config = {"from_attributes": True}
