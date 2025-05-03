# api/routers/historical.py - Router for historical data endpoints
from fastapi import APIRouter, HTTPException, Path, Query, Depends, status
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session

from api.models.historical import EODDataList, FeatureDataList
from api.dependencies.db import get_db
from api.services.historical_service import get_eod_data, get_feature_data

router = APIRouter()


@router.get("/eod/{symbol}", response_model=EODDataList)
async def get_historical_eod_data(symbol: str = Path(..., description="Trading symbol"), from_date: Optional[date] = Query(None, description="Start date (inclusive)"), to_date: Optional[date] = Query(None, description="End date (inclusive)"), limit: int = Query(100, description="Maximum number of records to return"), db: Session = Depends(get_db)):
    """Get historical EOD (End of Day) data for a symbol"""
    # Set default date range if not provided
    if not to_date:
        to_date = date.today()
    if not from_date:
        from_date = to_date - timedelta(days=30)

    data = get_eod_data(db, symbol, from_date, to_date, limit)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No historical data found for {symbol} in the specified date range")

    return EODDataList(data=data, count=len(data))


@router.get("/features/{symbol}", response_model=FeatureDataList)
async def get_historical_feature_data(symbol: str = Path(..., description="Trading symbol"), from_date: Optional[date] = Query(None, description="Start date (inclusive)"), to_date: Optional[date] = Query(None, description="End date (inclusive)"), features: Optional[List[str]] = Query(None, description="Specific features to include"), limit: int = Query(100, description="Maximum number of records to return"), db: Session = Depends(get_db)):
    """Get calculated feature data for a symbol"""
    # Set default date range if not provided
    if not to_date:
        to_date = date.today()
    if not from_date:
        from_date = to_date - timedelta(days=30)

    data = get_feature_data(db, symbol, from_date, to_date, features, limit)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No feature data found for {symbol} in the specified date range")

    return FeatureDataList(data=data, count=len(data))
