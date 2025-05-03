# api/models/symbol.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SymbolBase(BaseModel):
    """Base symbol fields"""

    trading_symbol: str
    exchange: str
    name: str
    instrument_type: str


class SymbolCreate(SymbolBase):
    """Fields required to create a symbol"""

    security_id: str
    segment: str
    lot_size: Optional[int] = None
    fo_eligible: bool = False


class SymbolUpdate(BaseModel):
    """Fields that can be updated"""

    name: Optional[str] = None
    active: Optional[bool] = None
    fo_eligible: Optional[bool] = None
    lot_size: Optional[int] = None


class Symbol(SymbolBase):
    """Symbol response model"""

    id: int
    security_id: str
    segment: str
    lot_size: Optional[int] = None
    active: bool
    fo_eligible: bool
    created_at: datetime

    class Config:
        from_attributes = True
