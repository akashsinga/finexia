# core/predict/daily_predictor.py

import os
import joblib
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models.feature_data import FeatureData
from db.models.prediction_results import PredictionResult
from db.models.symbol import Symbol
from core.config import DAILY_MODELS_DIR, STRONG_MOVE_CONFIDENCE_THRESHOLD

def load_latest_features_for_symbol(session: Session, symbol: str) -> pd.DataFrame:
    """Fetch the latest feature row for the given symbol."""
    feature = session.query(FeatureData).filter(FeatureData.trading_symbol == symbol).order_by(FeatureData.date.desc()).first()
    if not feature:
        return pd.DataFrame()

    feature_dict = {col.name: getattr(feature, col.name) for col in FeatureData.__table__.columns if col.name not in ["id"]}
    return pd.DataFrame([feature_dict])

def load_model(symbol: str, model_type: str):
    """Load move or direction model for a symbol."""
    model_path = os.path.join(DAILY_MODELS_DIR, f"{symbol}_{model_type}.pkl")
    if not os.path.exists(model_path):
        print(f"[WARNING] Model not found: {model_path}")
        return None
    return joblib.load(model_path)

def predict_for_one_symbol(symbol: str):
    session: Session = SessionLocal()

    try:
        print(f"[INFO] Predicting for {symbol}...")

        features_df = load_latest_features_for_symbol(session, symbol)
        if features_df.empty:
            print(f"[WARNING] No feature data found for {symbol}. Skipping.")
            return

        move_model = load_model(symbol, "move")
        if move_model is None:
            print(f"[WARNING] Move model missing for {symbol}. Skipping.")
            return

        feature_cols = [col for col in features_df.columns if col not in ["trading_symbol", "exchange", "date"]]
        X = features_df[feature_cols]

        # After move_probs prediction:
        move_probs = move_model.predict_proba(X)[0]
        strong_move_confidence = float(move_probs[1])  # ← Add float conversion here

        direction_prediction = None
        direction_confidence = None

        if strong_move_confidence >= STRONG_MOVE_CONFIDENCE_THRESHOLD:
            direction_model = load_model(symbol, "direction")
            if direction_model:
                dir_probs = direction_model.predict_proba(X)[0]
                direction_prediction = "UP" if dir_probs[1] > dir_probs[0] else "DOWN"
                direction_confidence = float(max(dir_probs[0], dir_probs[1]))  # ← Add float conversion here

            else:
                print(f"[WARNING] Direction model missing for {symbol}. Skipping direction prediction.")

        # Insert prediction into prediction_results
        latest_date = features_df.iloc[0]["date"]

        prediction = PredictionResult(
            trading_symbol=symbol,
            date=latest_date,
            strong_move_confidence=strong_move_confidence,
            direction_prediction=direction_prediction,
            direction_confidence=direction_confidence
        )

        # First delete existing prediction for same symbol and date (safe overwrite)
        session.query(PredictionResult).filter(PredictionResult.trading_symbol == symbol, PredictionResult.date == latest_date).delete()
        session.add(prediction)
        session.commit()

        print(f"[INFO] Prediction saved for {symbol} - Move Confidence: {strong_move_confidence:.2f}, Direction: {direction_prediction}, Direction Confidence: {direction_confidence}")

    except Exception as e:
        print(f"[ERROR] Prediction failed for {symbol}: {e}")
        session.rollback()
    finally:
        session.close()

def predict_all_symbols():
    session: Session = SessionLocal()

    try:
        symbols = session.query(Symbol.trading_symbol).filter(Symbol.active == True).all()
        if not symbols:
            print("[WARNING] No active symbols found. Exiting prediction.")
            return

        for sym in symbols:
            predict_for_one_symbol(sym.trading_symbol)

    except Exception as e:
        print(f"[ERROR] Failed during bulk prediction: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    predict_all_symbols()
