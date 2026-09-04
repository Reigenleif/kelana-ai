from datetime import datetime

from database import Base
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    destination = Column(String, nullable=False)
    days = Column(Integer, nullable=False)
    budget = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    daily_budget = Column(Float, nullable=False)
    ai_recommendation = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", foreign_keys=[user_id])


class TripBase(BaseModel):
    destination: str = Field(..., min_length=1)
    days: int = Field(..., gt=0)
    budget: float = Field(..., gt=0)
    category: str = Field(..., min_length=1)
    daily_budget: float | None = Field(default=None, gt=0)
    ai_recommendation: str | None = None


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    destination: str | None = Field(default=None, min_length=1)
    days: int | None = Field(default=None, gt=0)
    budget: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, min_length=1)
    daily_budget: float | None = Field(default=None, gt=0)
    ai_recommendation: str | None = None


class TripOut(TripBase):
    id: int
    user_id: int
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)
