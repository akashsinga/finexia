# api/services/system_service.py
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
import os

from db.models.prediction_results import PredictionResult
from db.models.model_performance import ModelPerformance
from core.config import DAILY_MODELS_DIR


def get_system_stats(db: Session) -> Dict[str, Any]:
    """Get system statistics"""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)

    # Latest predictions
    total_predictions = db.query(PredictionResult).count()
    today_predictions = db.query(PredictionResult).filter(PredictionResult.date == today).count()
    yesterday_predictions = db.query(PredictionResult).filter(PredictionResult.date == yesterday).count()

    # Verified predictions
    verified_count = db.query(PredictionResult).filter(PredictionResult).count()

    verified_percent = (verified_count / total_predictions * 100) if total_predictions > 0 else 0

    # Direction predictions
    direction_count = db.query(PredictionResult).filter(PredictionResult.direction_prediction.isnot(None)).count()

    # Recent model training activity (from model performance table)
    recent_training = db.query(ModelPerformance).filter(ModelPerformance.training_date >= last_week).count()

    # Model files info
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(DAILY_MODELS_DIR):
        for file in files:
            if file.endswith(".pkl"):
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                file_count += 1

    # Convert to MB
    total_size_mb = total_size / (1024 * 1024)

    return {"total_predictions": total_predictions, "today_predictions": today_predictions, "yesterday_predictions": yesterday_predictions, "verified_predictions": verified_count, "verified_prediction_percent": verified_percent, "direction_predictions": direction_count, "recent_model_training_count": recent_training, "model_directory_size_mb": total_size_mb, "model_file_count": file_count}


def check_database_status(db: Session) -> str:
    """Check database connection status"""
    try:
        # Try a simple query
        db.execute("SELECT 1").fetchone()
        return "connected"
    except Exception as e:
        return e
