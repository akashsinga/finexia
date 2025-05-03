# api/services/historical_service.py
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional

from db.models.eod_data import EODData
from db.models.feature_data import FeatureData
from api.models.historical import EODDataResponse, FeatureDataResponse


def get_eod_data(db: Session, symbol: str, from_date: date, to_date: date, limit: int = 100) -> List[EODDataResponse]:
    """Get historical EOD data for a symbol within date range"""
    query = db.query(EODData).filter(EODData.trading_symbol == symbol, EODData.date >= from_date, EODData.date <= to_date)

    # Sort by date descending (newest first)
    query = query.order_by(EODData.date.desc())

    # Apply limit
    data = query.limit(limit).all()

    return data


def get_feature_data(db: Session, symbol: str, from_date: date, to_date: date, features: Optional[List[str]] = None, limit: int = 100) -> List[FeatureDataResponse]:
    """Get historical feature data for a symbol within date range"""
    query = db.query(FeatureData).filter(FeatureData.trading_symbol == symbol, FeatureData.date >= from_date, FeatureData.date <= to_date)

    # Sort by date descending (newest first)
    query = query.order_by(FeatureData.date.desc())

    # Apply limit
    data = query.limit(limit).all()

    # Convert to response models with specific features if requested
    result = []
    for item in data:
        # Extract features as dictionary
        feature_dict = {}
        # If no specific features requested, get all feature columns
        if not features:
            # Get all feature columns excluding metadata and string fields
            feature_cols = [col for col in item.__table__.columns.keys() 
                        if col not in ['id', 'trading_symbol', 'exchange', 'date', 'created_at', 'updated_at', 'source_tag']]
            for feature_name in feature_cols:
                if hasattr(item, feature_name):
                    feature_dict[feature_name] = getattr(item, feature_name)
        else:
            # Get only requested features
            for feature_name in features:
                if hasattr(item, feature_name) and feature_name != 'source_tag':
                    feature_dict[feature_name] = getattr(item, feature_name)

        response = FeatureDataResponse(id=item.id, trading_symbol=item.trading_symbol, exchange=item.exchange, date=item.date, features=feature_dict, created_at=item.created_at if hasattr(item, "created_at") else None)
        result.append(response)

    return result
