# api/models/historical.py
from pydantic import BaseModel
from typing import Any, List, Dict
from datetime import date, datetime


class EODDataBase(BaseModel):
    trading_symbol: str
    exchange: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


class EODDataResponse(EODDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EODDataList(BaseModel):
    data: List[EODDataResponse]
    count: int


class FeatureDataBase(BaseModel):
    trading_symbol: str
    exchange: str
    date: date


class FeatureDataResponse(FeatureDataBase):
    id: int
    features: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class FeatureDataList(BaseModel):
    data: List[FeatureDataResponse]
    count: int
