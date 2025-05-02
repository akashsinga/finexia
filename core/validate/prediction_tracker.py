# core/validate/prediction_tracker.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.database import SessionLocal
from db.models.prediction_results import PredictionResult
from db.models.eod_data import EODData
from typing import Dict, List, Optional, Tuple
from core.config import DEFAULT_DAILY_STRONG_MOVE_THRESHOLD

def get_db_session() -> Session:
    """Creates and returns a database session."""
    return SessionLocal()

def update_prediction_results() -> Tuple[int, int]:
    """
    Daily job to verify predictions against actual price movements.
    Returns count of verified and total predictions checked.
    """
    session = get_db_session()
    verified_count, total_count = 0, 0
    
    try:
        # Get unverified predictions older than 1 day
        predictions = session.query(PredictionResult).filter(
            PredictionResult.verified == False,
            PredictionResult.date < datetime.now().date() - timedelta(days=1)
        ).all()
        
        total_count = len(predictions)
        
        for pred in predictions:
            # Get historical prices after prediction date
            prices = session.query(EODData.date,EODData.high,EODData.low,EODData.close).filter(EODData.trading_symbol == pred.trading_symbol,EODData.date > pred.date,EODData.date <= pred.date + timedelta(days=20)).order_by(EODData.date.asc()).all()
            
            if not prices:
                continue
                
            # Calculate max move from prediction date
            base_close = session.query(EODData.close).filter(EODData.trading_symbol == pred.trading_symbol,EODData.date == pred.date).scalar()
            
            if not base_close:
                continue
                
            # Calculate maximum moves
            max_up_move, max_down_move = 0, 0
            up_day, down_day = None, None
            
            for i, price in enumerate(prices):
                # Calculate up move
                up_pct = (price.high - base_close) / base_close * 100
                if up_pct > max_up_move:
                    max_up_move = up_pct
                    up_day = price.date
                
                # Calculate down move
                down_pct = (price.low - base_close) / base_close * 100
                if down_pct < max_down_move:
                    max_down_move = down_pct
                    down_day = price.date
            
            # Determine if prediction was verified
            threshold = DEFAULT_DAILY_STRONG_MOVE_THRESHOLD  # Use the same threshold as model training
            verified = False
            verification_date = None
            days_to_fulfill = None
            actual_move_percent = None
            actual_direction = None
            
            if pred.direction_prediction == "UP" and max_up_move >= threshold:
                verified = True
                verification_date = up_day
                days_to_fulfill = (up_day - pred.date).days
                actual_move_percent = max_up_move
                actual_direction = "UP"
            elif pred.direction_prediction == "DOWN" and abs(max_down_move) >= threshold:
                verified = True
                verification_date = down_day
                days_to_fulfill = (down_day - pred.date).days
                actual_move_percent = max_down_move
                actual_direction = "DOWN"
            elif max_up_move >= threshold or abs(max_down_move) >= threshold:
                # Move happened but direction was wrong
                verified = False
                if max_up_move > abs(max_down_move):
                    actual_move_percent = max_up_move
                    actual_direction = "UP"
                else:
                    actual_move_percent = max_down_move
                    actual_direction = "DOWN"
            
            # Update prediction record
            if verified or (len(prices) >= 10):  # Only mark as false after checking at least 10 days
                pred.verified = verified
                pred.verification_date = verification_date
                pred.actual_move_percent = actual_move_percent
                pred.actual_direction = actual_direction
                pred.days_to_fulfill = days_to_fulfill
                session.add(pred)
                verified_count += 1 if verified else 0
        
        session.commit()
        print(f"[INFO] Verified {verified_count} out of {total_count} predictions")
        
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Failed to update prediction results: {e}")
    finally:
        session.close()
        
    return verified_count, total_count

def analyze_prediction_timeframes(symbol: Optional[str] = None) -> Dict[str, Dict[str, float]]:
    """Analyzes how long it takes for predictions to come true."""
    session = get_db_session()
    
    try:
        query = """
            SELECT 
                trading_symbol,
                AVG(days_to_fulfill) as avg_days,
                MIN(days_to_fulfill) as min_days,
                MAX(days_to_fulfill) as max_days,
                COUNT(*) as count
            FROM prediction_results
            WHERE verified = true
            AND days_to_fulfill IS NOT NULL
        """
        
        if symbol:
            query += " AND trading_symbol = :symbol"
            params = {"symbol": symbol}
        else:
            query += " GROUP BY trading_symbol HAVING COUNT(*) >= 5"
            params = {}
            
        results = session.execute(text(query), params).fetchall()
        return {r[0]: {"avg_days": r[1], "min_days": r[2], "max_days": r[3], "count": r[4]} for r in results}
    
    except Exception as e:
        print(f"[ERROR] Failed to analyze prediction timeframes: {e}")
        return {}
    finally:
        session.close()

def get_prediction_accuracy_by_symbol() -> pd.DataFrame:
    """
    Get prediction accuracy metrics for all symbols.
    Returns a DataFrame with accuracy statistics.
    """
    session = get_db_session()
    
    try:
        query = """
            SELECT 
                trading_symbol,
                COUNT(*) as total_predictions,
                SUM(CASE WHEN verified = true THEN 1 ELSE 0 END) as correct_predictions,
                SUM(CASE WHEN verified = true AND direction_prediction = actual_direction THEN 1 ELSE 0 END) as correct_direction,
                AVG(CASE WHEN verified = true THEN days_to_fulfill ELSE NULL END) as avg_days_to_fulfill
            FROM prediction_results
            WHERE verified IS NOT NULL
            GROUP BY trading_symbol
            HAVING COUNT(*) >= 5
        """
        
        df = pd.read_sql(text(query), session.bind)
        
        if not df.empty:
            # Calculate accuracy metrics
            df["move_accuracy"] = df["correct_predictions"] / df["total_predictions"]
            df["direction_accuracy"] = df["correct_direction"] / df["correct_predictions"].replace(0, np.nan)
            
            # Sort by accuracy
            df = df.sort_values("move_accuracy", ascending=False)
        
        return df
        
    except Exception as e:
        print(f"[ERROR] Failed to get prediction accuracy: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def get_symbol_prediction_history(symbol: str, limit: int = 50) -> pd.DataFrame:
    """
    Get detailed prediction history for a specific symbol.
    Returns a DataFrame with prediction details and outcomes.
    """
    session = get_db_session()
    
    try:
        query = """
            SELECT 
                date,
                strong_move_confidence,
                direction_prediction,
                direction_confidence,
                verified,
                verification_date,
                actual_move_percent,
                actual_direction,
                days_to_fulfill
            FROM prediction_results
            WHERE trading_symbol = :symbol
            ORDER BY date DESC
            LIMIT :limit
        """
        
        df = pd.read_sql(text(query), session.bind, params={"symbol": symbol, "limit": limit})
        return df
        
    except Exception as e:
        print(f"[ERROR] Failed to get prediction history for {symbol}: {e}")
        return pd.DataFrame()
    finally:
        session.close()