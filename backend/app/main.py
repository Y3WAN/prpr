from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.database import engine, Base
from app.models import User, FoodTruck, Menu, Review
from app.routers import auth, trucks, reviews, recommendations
from app.config import settings

limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE food_trucks ADD COLUMN IF NOT EXISTS keywords TEXT"))
    yield


app = FastAPI(title="푸릉푸릉 API", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(trucks.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "푸릉푸릉 API"}
