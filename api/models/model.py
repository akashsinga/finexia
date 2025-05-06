# api/models/model.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime


class ModelTrainingRequest(BaseModel):
    move_classifier: Optional[str] = None
    direction_classifier: Optional[str] = None
    threshold: Optional[float] = None
    max_days: Optional[int] = None


class ModelTrainingResponse(BaseModel):
    status: str
    symbol: str
    message: str
    settings: Dict[str, Any]


class ModelStatusResponse(BaseModel):
    trading_symbol: str
    last_trained: date
    last_evaluated: Optional[date] = None
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    model_file: str
    file_size_kb: float
    last_modified: datetime


class ModelList(BaseModel):
    models: List[ModelStatusResponse]
    count: int


class ModelPerformanceRequest(BaseModel):
    top_n: int = 5 # Number of top models to return
    metric: str = "recall" # Metric to rank by (accuracy, precision, recall, f1_score)
    fo_eligible: bool = False

class ModelPerformanceResponse(BaseModel):
    trading_symbol: str
    model_type: str
    training_date: date
    evaluation_date: date
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    predictions_count: int
    successful_count: int
    features: List[str]
