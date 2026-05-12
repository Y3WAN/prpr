from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False, default="customer")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    truck = relationship("FoodTruck", back_populates="owner", uselist=False)
    reviews = relationship("Review", back_populates="user")
