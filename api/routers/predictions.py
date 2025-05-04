# api/routers/predictions.py

from fastapi import APIRouter, HTTPException, Path, Query, Depends, status
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from api.models.prediction import PredictionResponse, PredictionList, PredictionFilter, RefreshPredictionRequest, PredictionStats
from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user
from api.services.prediction_service import get_latest_prediction, get_predictions_by_date, refresh_prediction, get_verified_prediction_stats, get_prediction_summary_symbol

router = APIRouter()


@router.get("/{symbol}", response_model=PredictionResponse)
async def get_prediction_for_symbol(symbol: str = Path(..., description="Trading Symbol"), db: Session = Depends(get_db)):
    """Get latest prediction for a specific symbol"""
    prediction = get_latest_prediction(db, symbol)
    if not prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No prediction found for {symbol}")
    return prediction


@router.get("/summary/{symbol}", response_model=dict)
async def get_prediction_summary_for_symbol(symbol: str = Path(..., description="Trading Symbol"), db: Session = Depends(get_db)):
    """Fetches prediction summary for specific symbol"""
    prediction_summary = get_prediction_summary_symbol(db, symbol)
    if not prediction_summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No prediction summary found for {symbol}")
    return prediction_summary


@router.get("", response_model=PredictionList)
async def list_predictions(prediction_date: Optional[date] = Query(None, description="Filter by prediction date"), verified: Optional[bool] = Query(None, description="Filter by verification status"), direction: Optional[str] = Query(None, description="Filter by direction (UP/DOWN)"), min_confidence: float = Query(0.5, description="Minimum confidence threshold"), fo_eligible: Optional[bool] = Query(None, description="Filter by F&O eligibility"), skip: int = Query(0, description="Number of records to skip"), limit: int = Query(100, description="Maximum number of records to return"), db: Session = Depends(get_db)):
    """Get predictions with various filters"""
    filters = PredictionFilter(prediction_date=prediction_date, verified=verified, direction=direction, min_confidence=min_confidence, fo_eligible=fo_eligible)

    predictions = get_predictions_by_date(db, filters, skip, limit)

    return PredictionList(predictions=predictions, count=len(predictions))


@router.post("/refresh/{symbol}", response_model=PredictionResponse)
async def refresh_prediction_for_symbol(symbol: str = Path(..., description="Trading Symbol"), request: RefreshPredictionRequest = RefreshPredictionRequest(), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Force refresh prediction for a specific symbol"""
    result = refresh_prediction(db, symbol, request.force_retrain)
    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to refresh predictions for {symbol}")

    return result


@router.get("/status/accuracy", response_model=dict)
async def get_prediction_accuracy_stats(start_date: Optional[date] = Query(None, description="Start date for accuracy period"), end_date: Optional[date] = Query(None, description="End date for accuracy period"), db: Session = Depends(get_db)):
    """Get prediction accuracy statistics"""
    stats = get_verified_prediction_stats(db, start_date, end_date)
    return stats
