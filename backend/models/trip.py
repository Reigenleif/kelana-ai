from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, Float, Integer, String

from database import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String, nullable=False)
    days = Column(Integer, nullable=False)
    budget = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    daily_budget = Column(Float, nullable=False)


class TripBase(BaseModel):
    destination: str = Field(..., min_length=1)
    days: int = Field(..., gt=0)
    budget: float = Field(..., gt=0)
    category: str = Field(..., min_length=1)
    daily_budget: float | None = Field(default=None, gt=0)


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    destination: str | None = Field(default=None, min_length=1)
    days: int | None = Field(default=None, gt=0)
    budget: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, min_length=1)
    daily_budget: float | None = Field(default=None, gt=0)


class TripOut(TripBase):
    id: int
    model_config = ConfigDict(from_attributes=True)