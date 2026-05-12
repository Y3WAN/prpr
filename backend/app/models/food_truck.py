from sqlalchemy import Column, Integer, String, Text, Float, Boolean, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class FoodTruck(Base):
    __tablename__ = "food_trucks"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_open = Column(Boolean, default=True)
    avg_rating = Column(Numeric(3, 2), default=0.0)
    review_count = Column(Integer, default=0)
    account_info = Column(String(255))
    image_url = Column(String(500))
    keywords = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="truck")
    menus = relationship("Menu", back_populates="truck", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="truck", cascade="all, delete-orphan")
