# api/models/prediction.py - Pydantic models for prediction data
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, datetime
from enum import Enum

class DirectionEnum(str, Enum):
    UP = "UP"
    DOWN = "DOWN"

class PredictionBase(BaseModel):
    """Base prediction fields"""
    trading_symbol: str
    date: date
    strong_move_confidence: float = Field(..., ge=0.0, le=1.0)

class PredictionCreate(PredictionBase):
    """Fields required to create a prediction"""
    direction_prediction: Optional[DirectionEnum] = None
    direction_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    model_config_hash: Optional[str] = None

    @validator('direction_confidence')
    def direction_confidence_requires_prediction(cls, v, values):
        if v is not None and values.get('direction_prediction') is None:
            raise ValueError('direction_confidence cannot be set without direction_prediction')
        return v

class PredictionResponse(PredictionBase):
    """Response model for prediction data"""
    id: int
    direction_prediction: Optional[DirectionEnum] = None
    direction_confidence: Optional[float] = None
    verified: Optional[bool] = None
    verification_date: Optional[date] = None
    actual_move_percent: Optional[float] = None
    actual_direction: Optional[DirectionEnum] = None
    days_to_fulfill: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class PredictionFilter(BaseModel):
    """Filter parameters for predictions"""
    prediction_date: Optional[date] = None
    verified: Optional[bool] = None
    direction: Optional[DirectionEnum] = None
    fo_eligible: Optional[bool] = None
    min_confidence: float = 0.5

class PredictionList(BaseModel):
    """List of prediction responses"""
    predictions: List[PredictionResponse]
    count: int

class PredictionStats(BaseModel):
    """Statistics about predictions"""
    total_predictions: int
    verified_predictions: int
    accuracy: float
    up_predictions: int
    down_predictions: int
    direction_accuracy: Optional[float] = None
    avg_days_to_fulfill: Optional[float] = None

class RefreshPredictionRequest(BaseModel):
    """Request to refresh a prediction"""
    force_retrain: bool = False