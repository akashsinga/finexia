# core/train/daily_trainer.py

import os
import pandas as pd
import joblib
from datetime import timedelta
from typing import List
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models.feature_data import FeatureData
from db.models.eod_data import EODData
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from core.config import (RANDOM_FOREST, XGBOOST, LIGHTGBM, DEFAULT_DAILY_STRONG_MOVE_THRESHOLD, RANDOM_FOREST_N_ESTIMATORS, RANDOM_FOREST_MAX_DEPTH, RANDOM_SEED, get_daily_model_path)

def get_classifier(classifier_name: str, scale_pos_weight: float = 1.0):
    """Create and return a single classifier instance."""
    if classifier_name == RANDOM_FOREST:
        return RandomForestClassifier(n_estimators=RANDOM_FOREST_N_ESTIMATORS, max_depth=RANDOM_FOREST_MAX_DEPTH, random_state=RANDOM_SEED, class_weight="balanced")
    elif classifier_name == XGBOOST:
        try:
            from xgboost import XGBClassifier
            return XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.05, min_child_weight=3, random_state=RANDOM_SEED, verbosity=0, scale_pos_weight=scale_pos_weight)
        except ImportError:
            raise ImportError("Please install xgboost: pip install xgboost")
    elif classifier_name == LIGHTGBM:
        try:
            from lightgbm import LGBMClassifier
            return LGBMClassifier(n_estimators=500, max_depth=6, learning_rate=0.05, min_child_weight=3, random_state=RANDOM_SEED)
        except ImportError:
            raise ImportError("Please install lightgbm: pip install lightgbm")
    else:
        raise ValueError(f"Unsupported classifier: {classifier_name}")

def train_daily_model(classifier_names: List[str] = [XGBOOST], threshold_percent=DEFAULT_DAILY_STRONG_MOVE_THRESHOLD):
    """
    Train one or multiple classifiers for predicting next day's strong movers.
    If multiple classifiers provided, trains a soft VotingClassifier.
    """

    session: Session = SessionLocal()

    # Load features
    print("[INFO] Loading feature data...")
    features = session.query(FeatureData).all()

    # Load EOD close prices
    print("[INFO] Loading close prices from EOD...")
    closes = session.query(EODData.trading_symbol, EODData.exchange, EODData.date, EODData.close).all()

    session.close()

    if not features or not closes:
        print("[ERROR] No feature or close data found!")
        return

    # Convert to DataFrames
    features_df = pd.DataFrame([{
        "trading_symbol": f.trading_symbol,
        "exchange": f.exchange,
        "date": f.date,
        "volatility_squeeze": f.volatility_squeeze,
        "trend_zone_strength": f.trend_zone_strength,
        "range_compression_ratio": f.range_compression_ratio,
        "volume_spike_ratio": f.volume_spike_ratio,
        "body_to_range_ratio": f.body_to_range_ratio,
        "distance_from_ema_5": f.distance_from_ema_5,
        "gap_pct": f.gap_pct,
        "return_3d": f.return_3d,
        "atr_5": f.atr_5,
        "hl_range": f.hl_range,
        "fo_eligible": f.fo_eligible  # (optional, not used in training)
    } for f in features])

    closes_df = pd.DataFrame([{
        "trading_symbol": c.trading_symbol, "exchange": c.exchange, "date": c.date, "close": c.close
    } for c in closes])

    if features_df.empty or closes_df.empty:
        print("[ERROR] Empty dataframes after loading.")
        return

    # Merge close prices into features
    df = features_df.merge(closes_df, on=["trading_symbol", "exchange", "date"], how="left")

    # Sort
    df = df.sort_values(["trading_symbol", "date"]).reset_index(drop=True)

    # Build target: Strong move and direction
    df["next_close"] = df.groupby("trading_symbol")["close"].shift(-1)
    df["percent_move_next_day"] = ((df["next_close"] - df["close"]) / df["close"]) * 100

    # Strong move (absolute move > threshold)
    df["strong_move_target"] = (df["percent_move_next_day"].abs() > threshold_percent).astype(int)

    # Direction (only if move happens)
    df["direction_target"] = (df["percent_move_next_day"] > 0).astype(int)

    # Drop rows where next close is NA
    df = df.dropna(subset=["strong_move_target", "direction_target"])

    # Drop unnecessary columns
    drop_cols = ["trading_symbol", "exchange", "date", "close", "next_close", "percent_move_next_day"]
    X = df.drop(columns=drop_cols + ["strong_move_target", "direction_target"])
    y = df["strong_move_target"]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y)

    # Calculate dynamic scale_pos_weight
    num_positive = (y_train == 1).sum()
    num_negative = (y_train == 0).sum()
    scale_pos_weight = num_negative / max(num_positive, 1)

    # Build classifiers
    classifiers_list = []
    for clf_name in classifier_names:
        clf = get_classifier(clf_name, scale_pos_weight=scale_pos_weight)
        classifiers_list.append((clf_name, clf))

    if len(classifiers_list) == 1:
        model = classifiers_list[0][1]
        print(f"[INFO] Training {classifier_names[0].upper()} Classifier...")
    else:
        model = VotingClassifier(estimators=classifiers_list, voting="soft")
        names_combined = "_".join(classifier_names)
        print(f"[INFO] Training VotingClassifier with {names_combined.upper()} (soft voting)...")

    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred)

    if hasattr(model, "feature_importances_"):
        feature_importances = model.feature_importances_
        feature_names = X_train.columns

        importance_df = pd.DataFrame({"feature": feature_names,"importance": feature_importances}).sort_values(by="importance", ascending=False)

        print("\n[INFO] Feature Importances:")
        print(importance_df.to_string(index=False))
    else:
        print("\n[INFO] Model does not support feature_importances_ attribute.")

    print("[INFO] Model evaluation:\n", report)

    # Save model
    model_filename = "_".join(classifier_names) + ".pkl"
    model_save_path = os.path.join(os.path.dirname(get_daily_model_path("dummy")), model_filename)
    joblib.dump(model, model_save_path)
    print(f"[INFO] Model saved to {model_save_path}")

if __name__ == "__main__":
    train_daily_model(classifier_names=[LIGHTGBM])
