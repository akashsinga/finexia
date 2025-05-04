# api/routers/models.py - Router for model management endpoints
from fastapi import APIRouter, HTTPException, Path, Query, Depends, BackgroundTasks, status
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from api.models.model import ModelStatusResponse, ModelList, ModelTrainingRequest, ModelTrainingResponse, ModelPerformanceResponse, ModelPerformanceRequest
from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user
from api.services.model_service import get_model_status, list_models, train_model_async, get_model_performance, get_model_performance_history
from api.config import settings

router = APIRouter()


@router.get("/{symbol}", response_model=ModelStatusResponse)
async def get_status_for_model(symbol: str = Path(..., description="Trading symbol"), db: Session = Depends(get_db)):
    """Get status and performance metrics for a specific model"""
    model = get_model_status(db, symbol)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No model found for {symbol}")
    return model


@router.get("", response_model=ModelList)
async def list_all_models(active_only: bool = Query(True, description="Only show active models"), min_accuracy: Optional[float] = Query(None, description="Filter by minimum accuracy"), skip: int = Query(0, description="Number of records to skip"), limit: int = Query(100, description="Maximum number of records to return"), db: Session = Depends(get_db)):
    """List all available models with filtering options"""
    models = list_models(db, active_only, min_accuracy, skip, limit)
    return ModelList(models=models, count=len(models))


@router.post("/train/{symbol}", response_model=ModelTrainingResponse)
async def train_model_for_symbol(background_tasks: BackgroundTasks, symbol: str = Path(..., description="Trading symbol"), request: ModelTrainingRequest = ModelTrainingRequest(), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Train or retrain a model for a specific symbol"""
    # Set default values if not provided
    move_classifier = request.move_classifier or settings.DEFAULT_MOVE_CLASSIFIER
    direction_classifier = request.direction_classifier or settings.DEFAULT_DIRECTION_CLASSIFIER
    threshold = request.threshold or settings.STRONG_MOVE_THRESHOLD
    max_days = request.max_days or settings.DEFAULT_MAX_DAYS

    # Run training in background
    background_tasks.add_task(train_model_async, db=db, symbol=symbol, move_classifier=move_classifier, direction_classifier=direction_classifier, threshold=threshold, max_days=max_days, user_id=current_user.id)

    return ModelTrainingResponse(status="training_started", symbol=symbol, message=f"Training started for {symbol}", settings={"move_classifier": move_classifier, "direction_classifier": direction_classifier, "threshold": threshold, "max_days": max_days})


@router.post("/performance", response_model=List[ModelPerformanceResponse])
async def get_overall_model_performance(request: ModelPerformanceRequest, db: Session = Depends(get_db)):
    """Get overall performance metrics for all models"""
    performance = get_model_performance(db, request.top_n, request.metric)
    return performance


@router.get("/{symbol}/history", response_model=List[ModelPerformanceResponse])
async def get_model_history(symbol: str = Path(..., description="Trading symbol"), start_date: Optional[date] = Query(None, description="Start date for history"), end_date: Optional[date] = Query(None, description="End date for history"), db: Session = Depends(get_db)):
    """Get historical performance metrics for a specific model"""
    history = get_model_performance_history(db, symbol, start_date, end_date)
    return history
