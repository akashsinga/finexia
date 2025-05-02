# core/validate/feedback_optimizer.py

import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
from sqlalchemy import text
from db.database import SessionLocal
from core.validate.model_evaluator import identify_worst_performing_models, get_model_performance_metrics
from core.train.daily_trainer import train_models_for_one_symbol
from core.config import LIGHTGBM, XGBOOST, DEFAULT_DAILY_STRONG_MOVE_THRESHOLD, STRONG_MOVE_CONFIDENCE_THRESHOLD
from typing import Dict, List, Optional, Any, Tuple

def recommend_retraining_candidates() -> Dict[str, Dict]:
    """Identify symbols that would benefit from retraining with feedback."""
    # Get performance metrics
    df = get_model_performance_metrics()
    
    if df.empty:
        return {}
    
    # Identify candidates for retraining
    candidates = {}
    
    # Models with sufficient data but low accuracy
    low_accuracy = df[(df['accuracy'] < 0.5) & (df['total_predictions'] >= 20)]
    for _, row in low_accuracy.iterrows():
        candidates[row['trading_symbol']] = {
            "reason": "Low accuracy",
            "accuracy": row['accuracy'],
            "predictions": row['total_predictions'],
            "priority": "high" if row['accuracy'] < 0.4 else "medium"
        }
    
    # Models with good accuracy but poor direction prediction
    direction_issues = df[(df['accuracy'] >= 0.5) & (df['direction_accuracy'] < 0.6)]
    for _, row in direction_issues.iterrows():
        candidates[row['trading_symbol']] = {
            "reason": "Poor direction prediction",
            "accuracy": row['accuracy'],
            "direction_accuracy": row['direction_accuracy'],
            "priority": "medium"
        }
    
    return candidates

def analyze_optimal_parameters(symbol: str) -> Dict[str, Any]:
    """
    Analyze prediction history to determine optimal parameters for a symbol.
    Returns dictionary with recommended threshold and other parameters.
    """
    session = SessionLocal()
    
    try:
        # Get historical prediction performance
        query = """
            SELECT 
                verified, 
                strong_move_confidence,
                direction_prediction,
                actual_direction,
                actual_move_percent,
                days_to_fulfill
            FROM prediction_results
            WHERE trading_symbol = :symbol
            AND actual_move_percent IS NOT NULL
            ORDER BY date DESC
            LIMIT 100
        """
        
        df = pd.read_sql(text(query), session.bind, params={"symbol": symbol})
        
        if df.empty:
            return {
                "threshold_percent": DEFAULT_DAILY_STRONG_MOVE_THRESHOLD,
                "confidence_threshold": STRONG_MOVE_CONFIDENCE_THRESHOLD,
                "min_days": 1,
                "max_days": 10,
                "enough_data": False
            }
            
        # Find optimal confidence threshold
        confidence_levels = np.arange(0.3, 0.9, 0.05)
        best_accuracy = 0
        optimal_confidence = 0.5  # Default
            
        for level in confidence_levels:
            subset = df[df['strong_move_confidence'] >= level]
            if len(subset) < 10:  # Need enough samples
                continue
                
            accuracy = subset['verified'].mean()
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                optimal_confidence = level
                
        # Find optimal move threshold based on actual moves
        moves = df['actual_move_percent'].dropna().abs()
        if len(moves) >= 20:
            # Use percentiles to determine thresholds
            move_percentiles = [np.percentile(moves, p) for p in [25, 50, 60, 75]]
            
            # Choose threshold based on distribution
            # Lower threshold if moves tend to be smaller
            if move_percentiles[1] < DEFAULT_DAILY_STRONG_MOVE_THRESHOLD * 0.75:
                optimal_threshold = max(move_percentiles[1], 3.0)  # Don't go below 3%
            # Higher threshold if moves tend to be larger
            elif move_percentiles[1] > DEFAULT_DAILY_STRONG_MOVE_THRESHOLD * 1.25:
                optimal_threshold = min(move_percentiles[1], 12.0)  # Don't go above 12%
            else:
                optimal_threshold = DEFAULT_DAILY_STRONG_MOVE_THRESHOLD
        else:
            optimal_threshold = DEFAULT_DAILY_STRONG_MOVE_THRESHOLD
            
        # Determine optimal time window
        fulfill_days = df['days_to_fulfill'].dropna()
        
        if len(fulfill_days) >= 10:
            p90 = np.percentile(fulfill_days, 90)
            max_days = min(int(round(p90)), 15)  # Cap at 15 days
            min_days = max(1, int(fulfill_days.min()))
        else:
            min_days = 1
            max_days = 10
            
        return {
            "threshold_percent": float(optimal_threshold),
            "confidence_threshold": float(optimal_confidence),
            "min_days": min_days,
            "max_days": max_days,
            "enough_data": len(df) >= 20,
            "accuracy_potential": float(best_accuracy)
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to analyze optimal parameters for {symbol}: {e}")
        return {
            "threshold_percent": DEFAULT_DAILY_STRONG_MOVE_THRESHOLD,
            "error": str(e)
        }
    finally:
        session.close()

def retrain_with_feedback(symbol: str, custom_threshold: Optional[float] = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Retrain a specific symbol's model using validation feedback.
    Returns True if retraining was successful and the parameter dict used.
    """
    # Get optimal parameters
    if custom_threshold is not None:
        params = {
            "threshold_percent": custom_threshold,
            "min_days": 1,
            "max_days": 10
        }
    else:
        params = analyze_optimal_parameters(symbol)
        
    if params.get("error"):
        return False, params
    
    threshold_percent = params["threshold_percent"]
    min_days = params["min_days"]
    max_days = params["max_days"]
    
    print(f"[INFO] Retraining {symbol} with threshold {threshold_percent}%, window {min_days}-{max_days} days")
        
    # Retrain the model with optimized parameters
    try:
        result = train_models_for_one_symbol(
            symbol=symbol,
            move_classifiers=[LIGHTGBM, XGBOOST],  # Use ensemble
            direction_classifiers=[LIGHTGBM, XGBOOST],  # Use ensemble
            threshold_percent=threshold_percent,
            min_days=min_days,
            max_days=max_days
        )
        
        success = result["status"] == "success" or result["status"] == "partial_success"
        
        # Add training metrics to results
        params["training_result"] = {
            "status": result["status"],
            "move_metrics": result.get("move_metrics", {}),
            "direction_metrics": result.get("direction_metrics", {})
        }
        
        return success, params
        
    except Exception as e:
        print(f"[ERROR] Failed to retrain {symbol} with feedback: {e}")
        params["error"] = str(e)
        return False, params

def batch_optimize_models(max_symbols: int = 10, prioritize: bool = True) -> Dict[str, Any]:
    """
    Optimize multiple models based on their performance.
    Returns dictionary with optimization results.
    """
    # Get candidates for retraining
    candidates = recommend_retraining_candidates()
    
    if not candidates:
        return {"status": "no_candidates", "message": "No symbols identified for retraining"}
    
    # Prioritize symbols if requested
    if prioritize:
        high_priority = {sym: data for sym, data in candidates.items() if data.get("priority") == "high"}
        symbols_to_train = list(high_priority.keys())[:max_symbols]
    else:
        symbols_to_train = list(candidates.keys())[:max_symbols]
    
    print(f"[INFO] Optimizing {len(symbols_to_train)} models: {', '.join(symbols_to_train)}")
    
    # Train models
    results = {}
    for symbol in symbols_to_train:
        success, params = retrain_with_feedback(symbol)
        results[symbol] = {
            "success": success,
            "parameters": params
        }
    
    # Summarize results
    successful = sum(1 for r in results.values() if r["success"])
    
    return {
        "status": "completed",
        "total": len(symbols_to_train),
        "successful": successful,
        "failed": len(symbols_to_train) - successful,
        "details": results
    }

def update_model_config(symbol: str, threshold_percent: float, min_days: int = 1, max_days: int = 10) -> bool:
    """
    Update configuration parameters for a symbol model.
    Returns True if successful.
    """
    try:
        # Get model paths
        from core.config import get_daily_model_path
        move_path = get_daily_model_path(symbol, "move")
        direction_path = get_daily_model_path(symbol, "direction")
        
        # Update move model config
        if os.path.exists(move_path):
            model_data = joblib.load(move_path)
            
            if isinstance(model_data, dict) and "model" in model_data:
                # New format with metadata
                model_data["threshold_percent"] = threshold_percent
                model_data["min_days"] = min_days
                model_data["max_days"] = max_days
                model_data["config_updated_date"] = datetime.now().strftime("%Y-%m-%d")
                
                # Save updated model
                joblib.dump(model_data, move_path)
                print(f"[INFO] Updated configuration for {symbol} move model")
            else:
                print(f"[WARNING] Model for {symbol} uses old format, cannot update config")
                
        # Update direction model config
        if os.path.exists(direction_path):
            dir_model_data = joblib.load(direction_path)
            
            if isinstance(dir_model_data, dict) and "model" in dir_model_data:
                # New format with metadata
                dir_model_data["threshold_percent"] = threshold_percent
                dir_model_data["min_days"] = min_days
                dir_model_data["max_days"] = max_days
                dir_model_data["config_updated_date"] = datetime.now().strftime("%Y-%m-%d")
                
                # Save updated model
                joblib.dump(dir_model_data, direction_path)
                
        return True
            
    except Exception as e:
        print(f"[ERROR] Failed to update model config for {symbol}: {e}")
        return False