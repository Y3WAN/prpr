from sqlalchemy import Column, Integer, SmallInteger, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(Integer, ForeignKey("food_trucks.id", ondelete="CASCADE"), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    rating = Column(SmallInteger, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint("truck_id", "user_id"),)

    truck = relationship("FoodTruck", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
