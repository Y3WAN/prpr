from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    nickname: str = Field(..., min_length=1, max_length=50)
    role: Literal["customer", "owner"] = "customer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    nickname: str
    role: str

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
