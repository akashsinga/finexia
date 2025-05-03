# api/models/system.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SystemStatusResponse(BaseModel):
    status: str
    server_time: datetime
    database_status: str
    total_predictions: int
    today_predictions: int
    yesterday_predictions: int
    verified_predictions: int
    verified_prediction_percent: float
    direction_predictions: int
    recent_model_training_count: int
    model_directory_size_mb: float
    model_file_count: int


class PipelineStatusResponse(BaseModel):
    status: str
    message: str
    start_time: datetime
    requested_by: str
    estimated_duration_minutes: int
    steps: List[str]


class PipelineRunRequest(BaseModel):
    force: bool = False
    steps: Optional[List[str]] = None
