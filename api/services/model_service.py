# api/services/model_service.py - Business logic for model management
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, datetime
from typing import List, Optional, Dict, Any
import os
import asyncio

from db.models.model_performance import ModelPerformance
from db.models.symbol import Symbol
from core.config import DAILY_MODELS_DIR, LIGHTGBM
from core.train.daily_trainer import train_models_for_one_symbol
from api.models.model import ModelStatusResponse, ModelPerformanceResponse


def get_model_status(db: Session, symbol: str) -> Optional[ModelStatusResponse]:
    """Get status and metrics for a specific model"""
    # Check if model exists
    model_path = os.path.join(DAILY_MODELS_DIR, f"{symbol}_move.pkl")

    if not os.path.exists(model_path):
        return None

    # Get latest performance metrics
    performance = db.query(ModelPerformance).filter(ModelPerformance.trading_symbol == symbol, ModelPerformance.model_type == "move").order_by(ModelPerformance.evaluation_date.desc()).first()

    # Get model file info
    last_modified = datetime.fromtimestamp(os.path.getmtime(model_path))

    # Build response
    response = ModelStatusResponse(trading_symbol=symbol, last_trained=performance.training_date if performance else last_modified.date(), last_evaluated=performance.evaluation_date if performance else None, accuracy=performance.accuracy if performance else None, precision=performance.precision if performance else None, recall=performance.recall if performance else None, f1_score=performance.f1_score if performance else None, model_file=os.path.basename(model_path), file_size_kb=os.path.getsize(model_path) / 1024, last_modified=last_modified)

    return response


def list_models(db: Session, active_only: bool = True, min_accuracy: Optional[float] = None, skip: int = 0, limit: int = 100) -> List[ModelStatusResponse]:
    """List all available models with filtering options"""
    # Get symbols to check
    symbol_query = db.query(Symbol.trading_symbol)

    if active_only:
        symbol_query = symbol_query.filter(Symbol.active)

    symbols = [s.trading_symbol for s in symbol_query.all()]

    # Get status for each model
    models = []
    for symbol in symbols:
        status = get_model_status(db, symbol)
        if status:
            # Filter by minimum accuracy if specified
            if min_accuracy is not None and (status.accuracy is None or status.accuracy < min_accuracy):
                continue

            models.append(status)

    # Sort by accuracy (descending)
    models.sort(key=lambda x: x.accuracy if x.accuracy is not None else 0, reverse=True)

    # Apply pagination
    paginated_models = models[skip : skip + limit]

    return paginated_models


async def train_model_async(db: Session, symbol: str, move_classifier: str = LIGHTGBM, direction_classifier: str = LIGHTGBM, threshold: float = 3.0, min_days: int = 1, max_days: int = 5, user_id: Optional[int] = None) -> Dict[str, Any]:
    """Train a model asynchronously"""
    # Use run_in_executor to run CPU-bound training in a thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: train_models_for_one_symbol(symbol=symbol, move_classifiers=[move_classifier], direction_classifiers=[direction_classifier], threshold_percent=threshold, min_days=min_days, max_days=max_days))

    # Log training result
    # In a production system, you might want to save this to a database
    print(f"Training completed for {symbol} by user {user_id}: {result['status']}")

    return result


def get_model_performance(db: Session, top_n: int = 10, metric: str = "f1_score") -> List[ModelPerformanceResponse]:
    """Get performance metrics for all models, sorted by specified metric"""
    # Validate metric
    valid_metrics = ["accuracy", "precision", "recall", "f1_score"]
    if metric not in valid_metrics:
        metric = "f1_score"

    # Get latest performance for each model
    subquery = db.query(ModelPerformance.trading_symbol, func.max(ModelPerformance.evaluation_date).label("max_date")).group_by(ModelPerformance.trading_symbol).subquery()

    # Join with main table to get full performance data
    query = db.query(ModelPerformance).join(subquery, (ModelPerformance.trading_symbol == subquery.c.trading_symbol) & (ModelPerformance.evaluation_date == subquery.c.max_date))

    # Get "move" model performance only
    query = query.filter(ModelPerformance.model_type == "move")

    # Sort by specified metric
    if metric == "accuracy":
        query = query.order_by(desc(ModelPerformance.accuracy))
    elif metric == "precision":
        query = query.order_by(desc(ModelPerformance.precision))
    elif metric == "recall":
        query = query.order_by(desc(ModelPerformance.recall))
    else:  # f1_score
        query = query.order_by(desc(ModelPerformance.f1_score))

    # Limit to top N
    performances = query.limit(top_n).all()

    # Convert to response models
    result = []
    for perf in performances:
        # Convert features from JSON string
        import json

        features = json.loads(perf.effective_features) if perf.effective_features else []

        result.append(ModelPerformanceResponse(trading_symbol=perf.trading_symbol, model_type=perf.model_type, training_date=perf.training_date, evaluation_date=perf.evaluation_date, accuracy=perf.accuracy, precision=perf.precision, recall=perf.recall, f1_score=perf.f1_score, predictions_count=perf.predictions_count, successful_count=perf.successful_count, features=features))

    return result


def get_model_performance_history(db: Session, symbol: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[ModelPerformanceResponse]:
    """Get historical performance metrics for a specific model"""
    query = db.query(ModelPerformance).filter(ModelPerformance.trading_symbol == symbol, ModelPerformance.model_type == "move")

    if start_date:
        query = query.filter(ModelPerformance.evaluation_date >= start_date)

    if end_date:
        query = query.filter(ModelPerformance.evaluation_date <= end_date)

    # Sort by date
    query = query.order_by(ModelPerformance.evaluation_date.desc())

    performances = query.all()

    # Convert to response models
    result = []
    for perf in performances:
        # Convert features from JSON string
        import json

        features = json.loads(perf.effective_features) if perf.effective_features else []

        result.append(ModelPerformanceResponse(trading_symbol=perf.trading_symbol, model_type=perf.model_type, training_date=perf.training_date, evaluation_date=perf.evaluation_date, accuracy=perf.accuracy, precision=perf.precision, recall=perf.recall, f1_score=perf.f1_score, predictions_count=perf.predictions_count, successful_count=perf.successful_count, features=features))

    return result
