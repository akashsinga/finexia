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
from core.config import (RANDOM_FOREST, XGBOOST, LIGHTGBM,DEFAULT_DAILY_STRONG_MOVE_THRESHOLD,RANDOM_FOREST_N_ESTIMATORS, RANDOM_FOREST_MAX_DEPTH, RANDOM_SEED,get_daily_model_path)

def get_classifier(classifier_name: str):
    """Create and return a single classifier instance."""
    if classifier_name == RANDOM_FOREST:
        return RandomForestClassifier(n_estimators=RANDOM_FOREST_N_ESTIMATORS, max_depth=RANDOM_FOREST_MAX_DEPTH, random_state=RANDOM_SEED)
    elif classifier_name == XGBOOST:
        try:
            from xgboost import XGBClassifier
            return XGBClassifier(n_estimators=RANDOM_FOREST_N_ESTIMATORS, max_depth=RANDOM_FOREST_MAX_DEPTH, random_state=RANDOM_SEED, verbosity=0)
        except ImportError:
            raise ImportError("Please install xgboost: pip install xgboost")
    elif classifier_name == LIGHTGBM:
        try:
            from lightgbm import LGBMClassifier
            return LGBMClassifier(n_estimators=RANDOM_FOREST_N_ESTIMATORS, max_depth=RANDOM_FOREST_MAX_DEPTH, random_state=RANDOM_SEED)
        except ImportError:
            raise ImportError("Please install lightgbm: pip install lightgbm")
    else:
        raise ValueError(f"Unsupported classifier: {classifier_name}")

def train_daily_model(classifier_names: List[str] = [RANDOM_FOREST], threshold_percent=DEFAULT_DAILY_STRONG_MOVE_THRESHOLD):
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
        "trading_symbol": f.trading_symbol, "exchange": f.exchange, "date": f.date,
        "price_change_t_1": f.price_change_t_1, "gap_pct": f.gap_pct, "hl_range": f.hl_range, "body_to_range_ratio": f.body_to_range_ratio,
        "lower_wick_pct": f.lower_wick_pct, "upper_wick_pct": f.upper_wick_pct, "closing_strength": f.closing_strength,
        "distance_from_ema_5": f.distance_from_ema_5, "return_3d": f.return_3d, "return_5d": f.return_5d,
        "position_in_range_5d": f.position_in_range_5d, "atr_5": f.atr_5, "volume_spike_ratio": f.volume_spike_ratio,
        "range_compression_ratio": f.range_compression_ratio, "volatility_squeeze": f.volatility_squeeze,
        "trend_zone_strength": f.trend_zone_strength, "fo_eligible": f.fo_eligible
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

    # Build target: Strong move next day
    df["next_close"] = df.groupby("trading_symbol")["close"].shift(-1)
    df["percent_move_next_day"] = ((df["next_close"] - df["close"]) / df["close"]) * 100
    df["target"] = (df["percent_move_next_day"] > threshold_percent).astype(int)

    # Drop rows where target is NA
    df = df.dropna(subset=["target"])

    # Drop unnecessary columns
    drop_cols = ["trading_symbol", "exchange", "date", "close", "next_close", "percent_move_next_day"]
    X = df.drop(columns=drop_cols + ["target"])
    y = df["target"]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y)

    # Build classifiers
    classifiers_list = []
    for clf_name in classifier_names:
        clf = get_classifier(clf_name)
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
    print("[INFO] Model evaluation:\n", report)

    # Save model
    model_filename = "_".join(classifier_names) + ".pkl"
    model_save_path = os.path.join(os.path.dirname(get_daily_model_path("dummy")), model_filename)
    joblib.dump(model, model_save_path)
    print(f"[INFO] Model saved to {model_save_path}")

if __name__ == "__main__":
    train_daily_model()
