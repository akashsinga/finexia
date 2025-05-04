# api/services/prediction_service.py - Business logic for prediction operations
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional, Dict, Any

from db.models.prediction_results import PredictionResult
from db.models.symbol import Symbol
from core.predict.daily_predictor import predict_for_one_symbol
from core.train.daily_trainer import train_models_for_one_symbol
from api.models.prediction import PredictionFilter, PredictionResponse
import asyncio
from api.websockets.manager import connection_manager


def get_latest_prediction(db: Session, symbol: str) -> Optional[PredictionResponse]:
    """Get the latest prediction for a given symbol"""
    prediction = db.query(PredictionResult).filter(PredictionResult.trading_symbol == symbol).order_by(PredictionResult.date.desc()).first()

    if not prediction:
        return None

    return prediction


def get_predictions_by_date(db: Session, filters: PredictionFilter, skip: int = 0, limit: int = 100) -> List[PredictionResponse]:
    """Get predictions filtered by various criteria"""
    query = db.query(PredictionResult)

    # Apply filters
    if filters.prediction_date:
        query = query.filter(PredictionResult.date == filters.prediction_date)

    if filters.verified is not None:
        query = query.filter(PredictionResult.verified == filters.verified)

    if filters.direction:
        query = query.filter(PredictionResult.direction_prediction == filters.direction)

    if filters.min_confidence > 0:
        query = query.filter(PredictionResult.strong_move_confidence >= filters.min_confidence)

    # Add filter for fo_eligible
    if filters.fo_eligible is not None:
        # Join with Symbol table to check fo_eligible status
        query = query.join(Symbol, (PredictionResult.trading_symbol == Symbol.trading_symbol)).filter(Symbol.fo_eligible == filters.fo_eligible)

    # Add pagination
    predictions = query.order_by(PredictionResult.date.desc()).offset(skip).limit(limit).all()

    return predictions


def refresh_prediction(db: Session, symbol: str, force_retrain: bool = False) -> Optional[PredictionResponse]:
    """Force refresh a prediction for a symbol, optionally retraining the model"""
    # Verify symbol exists
    exists = db.query(Symbol).filter(Symbol.trading_symbol == symbol, Symbol.active).first()
    if not exists:
        return None

    # Optionally retrain model first
    if force_retrain:
        from core.config import LIGHTGBM

        train_result = train_models_for_one_symbol(symbol=symbol, move_classifiers=[LIGHTGBM], direction_classifiers=[LIGHTGBM])

        if train_result["status"] not in ["success", "partial_success"]:
            return None

    # Generate new prediction
    success = predict_for_one_symbol(symbol=symbol)
    if not success:
        return None

    # Fetch the newly created prediction
    prediction = get_latest_prediction(db, symbol)

    # Broadcast the prediction via WebSocket if available
    try:
        # Create a dict representation of the prediction for broadcasting
        if prediction:
            prediction_dict = {"date": prediction.date.isoformat(), "strong_move_confidence": prediction.strong_move_confidence, "direction_prediction": prediction.direction_prediction, "direction_confidence": prediction.direction_confidence}

            # Use create_task to run this asynchronously without waiting
            asyncio.create_task(connection_manager.broadcast(message={"type": "new_prediction", "symbol": symbol, "prediction": prediction_dict}, topic=f"predictions_{symbol}"))
    except ImportError:
        # WebSocket support not enabled, continue without broadcasting
        pass
    except Exception as e:
        # Log error but don't fail the prediction refresh
        import logging

        logging.getLogger("finexia-api").error(f"WebSocket broadcast error: {str(e)}")

    # Return the prediction
    return prediction


def get_verified_prediction_stats(db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
    """Get statistics about prediction accuracy"""
    # Build query
    query = db.query(PredictionResult)

    # Apply date filters if provided
    if start_date:
        query = query.filter(PredictionResult.date >= start_date)

    if end_date:
        query = query.filter(PredictionResult.date <= end_date)

    # Only include predictions that have been verified
    query = query.filter(PredictionResult.verified.is_not(None))

    # Execute query
    predictions = query.all()

    # Calculate metrics
    total_count = len(predictions)
    if total_count == 0:
        return {"total_predictions": 0, "verified_predictions": 0, "accuracy": 0.0, "up_predictions": 0, "down_predictions": 0}

    verified_count = sum(1 for p in predictions if p.verified)
    up_count = sum(1 for p in predictions if p.direction_prediction == "UP")
    down_count = sum(1 for p in predictions if p.direction_prediction == "DOWN")

    # Direction accuracy - only for predictions with direction
    direction_predictions = [p for p in predictions if p.direction_prediction and p.actual_direction]
    direction_correct = sum(1 for p in direction_predictions if p.verified and p.direction_prediction == p.actual_direction)

    # Days to fulfill
    days_to_fulfill = [p.days_to_fulfill for p in predictions if p.verified and p.days_to_fulfill]
    avg_days = sum(days_to_fulfill) / len(days_to_fulfill) if days_to_fulfill else None

    return {"total_predictions": total_count, "verified_predictions": verified_count, "accuracy": verified_count / total_count if total_count > 0 else 0.0, "up_predictions": up_count, "down_predictions": down_count, "direction_accuracy": direction_correct / len(direction_predictions) if direction_predictions else None, "avg_days_to_fulfill": avg_days}
