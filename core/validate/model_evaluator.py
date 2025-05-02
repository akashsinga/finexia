# core/validate/model_evaluator.py

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from sqlalchemy import text
from db.database import SessionLocal
from db.models.model_performance import ModelPerformance
from db.models.prediction_results import PredictionResult
from core.config import STRONG_MOVE_CONFIDENCE_THRESHOLD
from typing import Dict, List, Tuple, Optional, Any

def get_model_performance_metrics(min_confidence: float = STRONG_MOVE_CONFIDENCE_THRESHOLD,min_predictions: int = 10,days_back: int = 90) -> pd.DataFrame:
    """
    Calculate performance metrics for model predictions.
    Returns DataFrame with metrics by symbol.
    """
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
        print(f"[ERROR] Failed to get model performance metrics: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def identify_best_performing_models(min_accuracy: float = 0.6) -> List[str]:
    """Identify symbols with high performing models."""
    df = get_model_performance_metrics()
    
    if df.empty:
        return []
        
    best_models = df[df['accuracy'] >= min_accuracy]['trading_symbol'].tolist()
    return best_models

def identify_worst_performing_models(max_accuracy: float = 0.4) -> List[str]:
    """Identify symbols with poorly performing models."""
    df = get_model_performance_metrics()
    
    if df.empty:
        return []
        
    worst_models = df[df['accuracy'] <= max_accuracy]['trading_symbol'].tolist()
    return worst_models

def get_confidence_threshold_analysis(symbol: Optional[str] = None) -> pd.DataFrame:
    """
    Analyze how different confidence thresholds affect accuracy.
    Returns DataFrame with thresholds and corresponding accuracies.
    """
    session = SessionLocal()
    
    try:
        # Base query to get prediction results
        if symbol:
            query = f"""
                SELECT 
                    strong_move_confidence,
                    verified
                FROM prediction_results
                WHERE trading_symbol = '{symbol}'
                AND verified IS NOT NULL
            """
        else:
            query = """
                SELECT 
                    strong_move_confidence,
                    verified
                FROM prediction_results
                WHERE verified IS NOT NULL
            """
            
        df = pd.read_sql(text(query), session.bind)
        
        if df.empty:
            return pd.DataFrame()
            
        # Analyze different confidence thresholds
        thresholds = np.arange(0.1, 1.0, 0.05)
        results = []
        
        for threshold in thresholds:
            subset = df[df['strong_move_confidence'] >= threshold]
            
            if len(subset) < 5:  # Skip if too few samples
                continue
                
            accuracy = subset['verified'].mean()
            sample_count = len(subset)
            
            results.append({
                'threshold': threshold,
                'accuracy': accuracy,
                'sample_count': sample_count
            })
            
        return pd.DataFrame(results)
            
    except Exception as e:
        print(f"[ERROR] Failed to analyze confidence thresholds: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def save_model_performance(symbol: str,model_type: str,training_date: datetime,metrics: Dict[str, float],features: List[str],threshold: float) -> bool:
    """
    Save model performance metrics to database.
    Returns True if successful.
    """
    session = SessionLocal()
    
    try:
        # Check if we already have a record for this symbol and date
        existing = session.query(ModelPerformance).filter(
            ModelPerformance.trading_symbol == symbol,
            ModelPerformance.model_type == model_type,
            ModelPerformance.training_date == training_date.date()
        ).first()
        
        performance = existing or ModelPerformance(
            trading_symbol=symbol,
            model_type=model_type,
            training_date=training_date.date()
        )
        
        # Update fields
        performance.evaluation_date = datetime.now().date()
        performance.accuracy = metrics.get('accuracy', 0)
        performance.precision = metrics.get('precision', 0)
        performance.recall = metrics.get('recall', 0)
        performance.f1_score = metrics.get('f1', 0)
        performance.avg_days_to_fulfill = metrics.get('avg_days_to_fulfill')
        performance.sensitivity_threshold = threshold
        performance.effective_features = json.dumps(features)
        
        session.add(performance)
        session.commit()
        return True
        
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Failed to save model performance for {symbol}: {e}")
        return False
    finally:
        session.close()

def get_historical_performance(symbol: str, days_back: int = 90) -> pd.DataFrame:
    """
    Get historical performance metrics for a symbol.
    Returns DataFrame with performance over time.
    """
    session = SessionLocal()
    
    try:
        query = f"""
            SELECT 
                evaluation_date,
                accuracy,
                precision,
                recall,
                f1_score,
                avg_days_to_fulfill
            FROM model_performance
            WHERE trading_symbol = '{symbol}'
            AND evaluation_date >= CURRENT_DATE - INTERVAL '{days_back} days'
            ORDER BY evaluation_date
        """
        
        df = pd.read_sql(text(query), session.bind)
        return df
        
    except Exception as e:
        print(f"[ERROR] Failed to get historical performance for {symbol}: {e}")
        return pd.DataFrame()
    finally:
        session.close()