# core/predict/daily_predictor.py

import os
import joblib
import pandas as pd
from typing import Dict, Optional, Any
from functools import lru_cache
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.database import SessionLocal
from db.models.feature_data import FeatureData
from db.models.prediction_results import PredictionResult
from db.models.symbol import Symbol
from core.config import DAILY_MODELS_DIR, STRONG_MOVE_CONFIDENCE_THRESHOLD, MODEL_CACHE_SIZE

# Model cache to avoid reloading models
model_cache: Dict[str, Any] = {}

def get_db_session() -> Session:
    """Creates and returns a new database session."""
    return SessionLocal()

@lru_cache(maxsize=50)
def load_latest_features_for_symbol(symbol: str) -> pd.DataFrame:
    """Fetch the latest feature row for the given symbol with caching."""
    session = get_db_session()
    try:
        feature = session.query(FeatureData).filter(
            FeatureData.trading_symbol == symbol
        ).order_by(FeatureData.date.desc()).first()
        
        if not feature:
            return pd.DataFrame()

        # Convert SQLAlchemy model to dictionary
        feature_dict = {col.name: getattr(feature, col.name) for col in FeatureData.__table__.columns if col.name not in ["id"]}
        
        return pd.DataFrame([feature_dict])
    except SQLAlchemyError as e:
        print(f"[ERROR] Database error when loading features for {symbol}: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def load_model(symbol: str, model_type: str):
    """Load move or direction model for a symbol with caching."""
    cache_key = f"{symbol}_{model_type}"
    
    # Return from cache if available
    if cache_key in model_cache:
        return model_cache[cache_key]
        
    model_path = os.path.join(DAILY_MODELS_DIR, f"{symbol}_{model_type}.pkl")
    if not os.path.exists(model_path):
        print(f"[WARNING] Model not found: {model_path}")
        return None
        
    try:
        model = joblib.load(model_path)
        
        # Add to cache, with basic LRU management
        if len(model_cache) >= MODEL_CACHE_SIZE:
            # Remove a random item if cache is full
            model_cache.pop(next(iter(model_cache)))
        
        model_cache[cache_key] = model
        return model
    except Exception as e:
        print(f"[ERROR] Failed to load model {model_path}: {e}")
        return None

def save_prediction(session: Session, symbol: str, date, move_confidence: float, direction: Optional[str] = None, direction_confidence: Optional[float] = None) -> bool:
    """Save prediction to database with error handling."""
    try:
        # First delete existing prediction for same symbol and date (safe overwrite)
        session.query(PredictionResult).filter(
            PredictionResult.trading_symbol == symbol, 
            PredictionResult.date == date
        ).delete()
        
        # Create and add new prediction
        prediction = PredictionResult(
            trading_symbol=symbol,
            date=date,
            strong_move_confidence=move_confidence,
            direction_prediction=direction,
            direction_confidence=direction_confidence
        )
        session.add(prediction)
        session.commit()
        return True
    except SQLAlchemyError as e:
        print(f"[ERROR] Database error when saving prediction for {symbol}: {e}")
        session.rollback()
        return False

def predict_for_one_symbol(symbol: str) -> bool:
    """Generate and save predictions for one symbol with improved error handling."""
    session = get_db_session()
    success = False
    
    try:
        print(f"[INFO] Predicting for {symbol}...")

        features_df = load_latest_features_for_symbol(symbol)
        if features_df.empty:
            print(f"[WARNING] No feature data found for {symbol}. Skipping.")
            return False

        move_model = load_model(symbol, "move")
        if move_model is None:
            print(f"[WARNING] Move model missing for {symbol}. Skipping.")
            return False

        feature_cols = [col for col in features_df.columns  if col not in ["trading_symbol", "exchange", "date"]]
        X = features_df[feature_cols]

        # Predict move probability
        try:
            move_probs = move_model.predict_proba(X)[0]
            strong_move_confidence = float(move_probs[1])
        except Exception as e:
            print(f"[ERROR] Move prediction failed for {symbol}: {e}")
            return False

        direction_prediction = None
        direction_confidence = None

        # Only predict direction if move confidence is high enough
        if strong_move_confidence >= STRONG_MOVE_CONFIDENCE_THRESHOLD:
            direction_model = load_model(symbol, "direction")
            if direction_model:
                try:
                    dir_probs = direction_model.predict_proba(X)[0]
                    direction_prediction = "UP" if dir_probs[1] > dir_probs[0] else "DOWN"
                    direction_confidence = float(max(dir_probs[0], dir_probs[1]))
                except Exception as e:
                    print(f"[ERROR] Direction prediction failed for {symbol}: {e}")
            else:
                print(f"[WARNING] Direction model missing for {symbol}. Skipping direction prediction.")

        # Save prediction to database
        latest_date = features_df.iloc[0]["date"]
        success = save_prediction(
            session=session,
            symbol=symbol,
            date=latest_date,
            move_confidence=strong_move_confidence,
            direction=direction_prediction,
            direction_confidence=direction_confidence
        )

        if success:
            print(f"[INFO] Prediction saved for {symbol} - "
                 f"Move Confidence: {strong_move_confidence:.2f}, "
                 f"Direction: {direction_prediction}, "
                 f"Direction Confidence: {direction_confidence}")

    except Exception as e:
        print(f"[ERROR] Unexpected error in prediction for {symbol}: {e}")
        session.rollback()
        success = False
    finally:
        session.close()
        return success

def predict_all_symbols():
    """Run predictions for all active symbols with batching and progress tracking."""
    session = get_db_session()
    processed, successful = 0, 0
    
    try:
        # Get all active symbols
        symbols = session.query(Symbol.trading_symbol).filter(Symbol.active == True).all()
        if not symbols:
            print("[WARNING] No active symbols found. Exiting prediction.")
            return
            
        total_symbols = len(symbols)
        print(f"[INFO] Starting predictions for {total_symbols} symbols...")
        
        # Process each symbol
        for i, sym in enumerate(symbols):
            symbol = sym.trading_symbol
            success = predict_for_one_symbol(symbol)
            
            processed += 1
            if success:
                successful += 1
                
            # Log progress periodically
            if i % 10 == 0 or i == total_symbols - 1:
                print(f"[PROGRESS] Processed {processed}/{total_symbols} symbols "f"({successful} successful)")
                
    except Exception as e:
        print(f"[ERROR] Failed during bulk prediction: {e}")
    finally:
        session.close()
        print(f"[COMPLETE] Prediction run finished: {successful}/{processed} symbols successful")

if __name__ == "__main__":
    predict_all_symbols()
