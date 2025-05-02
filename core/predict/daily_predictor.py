# core/predict/daily_predictor.py

import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Optional, Any, List, Tuple
from functools import lru_cache
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from db.database import SessionLocal
from db.models.prediction_results import PredictionResult
from db.models.symbol import Symbol
from core.config import DAILY_MODELS_DIR, STRONG_MOVE_CONFIDENCE_THRESHOLD, MODEL_CACHE_SIZE

# Model cache to avoid reloading models
model_cache: Dict[str, Any] = {}

def timestamped_log(message: str):
    """Log message with timestamp."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def get_db_session() -> Session:
    """Creates and returns a new database session."""
    return SessionLocal()

@lru_cache(maxsize=50)
def load_latest_features_for_symbol(symbol: str) -> pd.DataFrame:
    """Fetch the latest feature row for the given symbol with caching."""
    session = get_db_session()
    try:
        # Use parameterized query for better security
        query = text("""
            SELECT * FROM features_data 
            WHERE trading_symbol = :symbol
            ORDER BY date DESC
            LIMIT 1
        """)
        result = session.execute(query, {"symbol": symbol})
        row = result.fetchone()
        
        if not row:
            return pd.DataFrame()

        # Convert result to dictionary
        feature_dict = dict(row._mapping)
        
        return pd.DataFrame([feature_dict])
    except SQLAlchemyError as e:
        timestamped_log(f"[ERROR] Database error when loading features for {symbol}: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def load_model_data(symbol: str, model_type: str) -> Optional[Dict[str, Any]]:
    """Load model data for a symbol with caching and metadata handling."""
    cache_key = f"{symbol}_{model_type}"
    
    # Return from cache if available
    if cache_key in model_cache:
        return model_cache[cache_key]
        
    model_path = os.path.join(DAILY_MODELS_DIR, f"{symbol}_{model_type}.pkl")
    if not os.path.exists(model_path):
        timestamped_log(f"[WARNING] Model not found: {model_path}")
        return None
        
    try:
        # Load model data (might be just the model or a dictionary with metadata)
        model_data = joblib.load(model_path)
        
        # Handle both old-style (just model) and new-style (dict with metadata) formats
        if isinstance(model_data, dict) and "model" in model_data:
            # New format with metadata
            result = model_data
        else:
            # Old format (just the model)
            result = {"model": model_data, "selected_features": None}
        
        # Add to cache, with basic LRU management
        if len(model_cache) >= MODEL_CACHE_SIZE:
            # Remove a random item if cache is full
            model_cache.pop(next(iter(model_cache)))
        
        model_cache[cache_key] = result
        return result
    except Exception as e:
        timestamped_log(f"[ERROR] Failed to load model {model_path}: {e}")
        return None

def save_prediction(symbol: str, date, move_confidence: float, direction: Optional[str] = None, direction_confidence: Optional[float] = None) -> bool:
    """Save prediction to database with error handling."""
    session = get_db_session()
    try:
        # First delete existing prediction for same symbol and date (safe overwrite)
        session.query(PredictionResult).filter(PredictionResult.trading_symbol == symbol, PredictionResult.date == date).delete()
        
        # Create and add new prediction
        prediction = PredictionResult(
            trading_symbol=symbol,
            date=date,
            strong_move_confidence=move_confidence,
            direction_prediction=direction,
            direction_confidence=direction_confidence,
            model_config_hash=generate_model_hash(symbol)  # Add model version tracking
        )
        session.add(prediction)
        session.commit()
        return True
    except SQLAlchemyError as e:
        timestamped_log(f"[ERROR] Database error when saving prediction for {symbol}: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def generate_model_hash(symbol: str) -> str:
    """Generate a simple hash to track model versions."""
    try:
        move_model_data = load_model_data(symbol, "move")
        if move_model_data and "training_date" in move_model_data:
            return move_model_data["training_date"]
        return datetime.now().strftime("%Y-%m-%d")
    except:
        return "unknown"

def prepare_features(features_df: pd.DataFrame, model_data: Dict[str, Any]) -> pd.DataFrame:
    """Prepare features using model-specific selected features."""
    if features_df.empty:
        return pd.DataFrame()
    
    # Ensure date column is datetime and excluded from features
    if 'date' in features_df.columns:
        features_df['date'] = pd.to_datetime(features_df['date'])
        
    # Get selected features if available
    selected_features = model_data.get("selected_features")
    
    if selected_features:
        # Use only selected features in the right order
        missing_features = [f for f in selected_features if f not in features_df.columns]
        if missing_features:
            timestamped_log(f"[WARNING] Missing features: {missing_features}")
            # Create missing columns with zeros
            for feat in missing_features:
                features_df[feat] = 0.0
        return features_df[selected_features]
    else:
        # Use all features excluding non-feature columns
        drop_cols = ["id", "trading_symbol", "exchange", "date", "created_at", "updated_at", "source_tag"]
        feature_cols = [col for col in features_df.columns if col not in drop_cols]
        return features_df[feature_cols]

def predict_for_one_symbol(symbol: str) -> bool:
    """Generate and save predictions for one symbol with improved error handling."""
    start_time = datetime.now()
    
    try:
        timestamped_log(f"[INFO] Predicting for {symbol}...")

        # Load latest features
        features_df = load_latest_features_for_symbol(symbol)
        if features_df.empty:
            timestamped_log(f"[WARNING] No feature data found for {symbol}. Skipping.")
            return False

        # Load move model
        move_model_data = load_model_data(symbol, "move")
        if move_model_data is None:
            timestamped_log(f"[WARNING] Move model missing for {symbol}. Skipping.")
            return False

        move_model = move_model_data["model"]
        
        # Prepare feature data for model
        X = prepare_features(features_df, move_model_data)
        if X.empty:
            timestamped_log(f"[WARNING] Failed to prepare features for {symbol}. Skipping.")
            return False

        # Predict move probability
        try:
            move_probs = move_model.predict_proba(X)[0]
            strong_move_confidence = float(move_probs[1])
        except Exception as e:
            timestamped_log(f"[ERROR] Move prediction failed for {symbol}: {e}")
            return False

        direction_prediction = None
        direction_confidence = None

        # Only predict direction if move confidence is high enough
        if strong_move_confidence >= STRONG_MOVE_CONFIDENCE_THRESHOLD:
            direction_model_data = load_model_data(symbol, "direction")
            if direction_model_data:
                try:
                    direction_model = direction_model_data["model"]
                    X_dir = prepare_features(features_df, direction_model_data)
                    
                    dir_probs = direction_model.predict_proba(X_dir)[0]
                    direction_prediction = "UP" if dir_probs[1] > dir_probs[0] else "DOWN"
                    direction_confidence = float(max(dir_probs[0], dir_probs[1]))
                except Exception as e:
                    timestamped_log(f"[ERROR] Direction prediction failed for {symbol}: {e}")
            else:
                timestamped_log(f"[WARNING] Direction model missing for {symbol}. Skipping direction prediction.")

        # Save prediction to database
        latest_date = features_df.iloc[0]["date"]
        success = save_prediction(
            symbol=symbol,
            date=latest_date,
            move_confidence=strong_move_confidence,
            direction=direction_prediction,
            direction_confidence=direction_confidence
        )

        if success:
            duration = (datetime.now() - start_time).total_seconds()
            confidence_str = f"{strong_move_confidence:.2f}"
            dir_str = f"{direction_prediction} ({direction_confidence:.2f})" if direction_prediction else "N/A"
            timestamped_log(f"[INFO] {symbol} prediction successful in {duration:.2f}s - Move: {confidence_str}, Direction: {dir_str}")
            return True
        else:
            timestamped_log(f"[ERROR] Failed to save prediction for {symbol}")
            return False

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        timestamped_log(f"[ERROR] Unexpected error in prediction for {symbol} after {duration:.2f}s: {e}")
        return False

def fetch_symbols_to_predict() -> List[str]:
    """Fetch list of symbols that need prediction, prioritizing those with models."""
    session = get_db_session()
    try:
        # Get all active symbols
        symbols = session.query(Symbol.trading_symbol).filter(Symbol.active == True).all()
        symbol_list = [s.trading_symbol for s in symbols]
        
        # Prioritize symbols that have models
        prioritized_symbols = []
        deferred_symbols = []
        
        for symbol in symbol_list:
            model_path = os.path.join(DAILY_MODELS_DIR, f"{symbol}_move.pkl")
            if os.path.exists(model_path):
                prioritized_symbols.append(symbol)
            else:
                deferred_symbols.append(symbol)
                
        return prioritized_symbols + deferred_symbols
    except SQLAlchemyError as e:
        timestamped_log(f"[ERROR] Failed to fetch symbols: {e}")
        return []
    finally:
        session.close()

def predict_all_symbols(max_workers: int = 8):
    """Run predictions for all active symbols with improved parallelization and progress tracking."""
    start_time = datetime.now()
    
    # Get symbols to predict
    symbols = fetch_symbols_to_predict()
    if not symbols:
        timestamped_log("[WARNING] No symbols to predict. Exiting.")
        return
        
    total_symbols = len(symbols)
    timestamped_log(f"[INFO] Starting predictions for {total_symbols} symbols with {max_workers} workers...")
    
    # Process symbols in parallel
    successful, failed = 0, 0
    
    # Use ThreadPoolExecutor for IO-bound operations
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(predict_for_one_symbol, symbol): symbol for symbol in symbols}
        
        for i, future in enumerate(as_completed(futures)):
            symbol = futures[future]
            
            try:
                success = future.result()
                
                if success:
                    successful += 1
                else:
                    failed += 1
                    
                # Log progress periodically
                if (i + 1) % 10 == 0 or (i + 1) == total_symbols:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    remaining = elapsed / (i + 1) * (total_symbols - i - 1)
                    completion_pct = (i + 1) / total_symbols * 100
                    
                    timestamped_log(f"[PROGRESS] {i+1}/{total_symbols} symbols ({completion_pct:.1f}%) "f"processed - Success: {successful}, Failed: {failed}, "f"Elapsed: {elapsed:.1f}s, Remaining: {remaining:.1f}s")
            except Exception as e:
                failed += 1
                timestamped_log(f"[ERROR] Exception during prediction for {symbol}: {e}")
    
    # Final stats
    duration = (datetime.now() - start_time).total_seconds()
    timestamped_log(f"[COMPLETE] Prediction run finished in {duration:.2f}s: {successful}/{total_symbols} successful")
    
    return successful, failed

def verify_predictions():
    """Verify predictions against latest data (if available)."""
    session = get_db_session()
    try:
        # Find most recent prediction date
        latest_date_result = session.query(PredictionResult.date).order_by(PredictionResult.date.desc()).first()
        
        if not latest_date_result:
            timestamped_log("[INFO] No predictions found for verification.")
            return
            
        latest_date = latest_date_result[0]
        
        # Count predictions for that date
        pred_count = session.query(PredictionResult).filter(PredictionResult.date == latest_date).count()
        
        # Check for symbols with high confidence
        high_conf_count = session.query(PredictionResult).filter(
            PredictionResult.date == latest_date,
            PredictionResult.strong_move_confidence >= STRONG_MOVE_CONFIDENCE_THRESHOLD
        ).count()
        
        timestamped_log(f"[INFO] Latest predictions for {latest_date}: {pred_count} total, {high_conf_count} high confidence")
        
    except SQLAlchemyError as e:
        timestamped_log(f"[ERROR] Failed to verify predictions: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # Set number of workers based on system capabilities
    import multiprocessing
    cpu_count = multiprocessing.cpu_count()
    workers = max(1, min(cpu_count - 1, 8))  # Use at most CPU count-1 or 8, whichever is lower
    
    predict_all_symbols(max_workers=workers)
    verify_predictions()