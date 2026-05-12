from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(Integer, ForeignKey("food_trucks.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())

    truck = relationship("FoodTruck", back_populates="menus")
