# scripts/run_validation_only.py

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import text
from db.database import SessionLocal

def timestamped_log(message: str):
    """Log message with timestamp."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
    
def check_prediction_results():
    """Check if there are any prediction results in the database."""
    session = SessionLocal()
    
    try:
        # Use proper SQLAlchemy query syntax
        from sqlalchemy import func
        from db.models.prediction_results import PredictionResult
        
        count = session.query(func.count(PredictionResult.id)).scalar()
        verified_count = session.query(func.count(PredictionResult.id)).filter(PredictionResult.verified == True).scalar()
        
        return {
            "total": count or 0,
            "verified": verified_count or 0
        }
    except Exception as e:
        print(f"[ERROR] Failed to check prediction results: {e}")
        return {"total": 0, "verified": 0}
    finally:
        session.close()

def get_model_performance_metrics(min_confidence=0.5, min_predictions=10, days_back=90):
    """Calculate performance metrics for model predictions."""
    session = SessionLocal()
    
    try:
        query = """
            SELECT 
                trading_symbol,
                COUNT(*) as total_predictions,
                SUM(CASE WHEN verified = true THEN 1 ELSE 0 END) as correct_predictions,
                SUM(CASE WHEN verified = true AND direction_prediction = actual_direction THEN 1 ELSE 0 END) as correct_direction,
                AVG(CASE WHEN verified = true THEN days_to_fulfill ELSE NULL END) as avg_days_to_fulfill,
                AVG(strong_move_confidence) as avg_confidence
            FROM prediction_results
            WHERE date >= CURRENT_DATE - INTERVAL ':days_back days'
            AND strong_move_confidence >= :min_confidence
            GROUP BY trading_symbol
            HAVING COUNT(*) >= :min_predictions
            ORDER BY SUM(CASE WHEN verified = true THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) DESC
        """
        
        df = pd.read_sql(
            text(query), 
            session.bind,
            params={
                "min_confidence": min_confidence,
                "min_predictions": min_predictions,
                "days_back": days_back
            }
        )
        
        # Calculate additional metrics
        if not df.empty:
            df['accuracy'] = df['correct_predictions'] / df['total_predictions']
            df['direction_accuracy'] = df['correct_direction'] / df['correct_predictions'].replace(0, np.nan)
            
        return df
        
    except Exception as e:
        timestamped_log(f"[ERROR] Failed to get model performance metrics: {e}")
        return pd.DataFrame()
    finally:
        session.close()

if __name__ == "__main__":
    timestamped_log("Running model validation only...")
    
    # Check prediction results
    counts = check_prediction_results()
    timestamped_log(f"Found {counts['total']} total predictions, {counts['verified']} verified.")
    
    # Only try to get metrics if there are verified predictions
    if counts['verified'] > 0:
        df = get_model_performance_metrics()
        # rest of your code...
    else:
        timestamped_log("No verified predictions found. Run the validation step first.")