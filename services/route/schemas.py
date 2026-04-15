from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class StopCreate(BaseModel):
    name: str
    lat: float
    lon: float


class StopUpdate(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class StopOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    lat: float
    lon: float
    created_at: datetime


class RouteCreate(BaseModel):
    name: str
    description: Optional[str] = ""


class RouteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class RouteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str]
    created_at: datetime


class RouteStopCreate(BaseModel):
    stop_id: str
    sequence: int


class RouteStopOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    route_id: str
    stop_id: str
    sequence: int
    created_at: datetime
