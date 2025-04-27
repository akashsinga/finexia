# core/train/daily_trainer.py

import os
import pandas as pd
import joblib
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models.feature_data import FeatureData
from db.models.eod_data import EODData
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from core.config import (RANDOM_FOREST, XGBOOST, LIGHTGBM, DEFAULT_DAILY_STRONG_MOVE_THRESHOLD, RANDOM_FOREST_N_ESTIMATORS, RANDOM_FOREST_MAX_DEPTH, RANDOM_SEED, get_daily_model_path)

def timestamped_log(message: str):
    """Utility to print logs with timestamps."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{now}] {message}")

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

def train_direction_model(df: pd.DataFrame, feature_cols: List[str], classifier_names: List[str]):
    """Train and save the Direction Model (only on strong movers)."""
    timestamped_log("Starting Direction Model training...")

    df_direction = df[df["strong_move_target"] == 1].copy()

    if len(df_direction) < 50:
        timestamped_log("Not enough strong movers to train Direction Model. Skipping.")
        return

    X_dir = df_direction[feature_cols]
    y_dir = df_direction["direction_target"]

    X_dir_train, X_dir_test, y_dir_train, y_dir_test = train_test_split(X_dir, y_dir, test_size=0.2, random_state=RANDOM_SEED, stratify=y_dir)

    num_positive = (y_dir_train == 1).sum()
    num_negative = (y_dir_train == 0).sum()
    scale_pos_weight = num_negative / max(num_positive, 1)

    classifiers_list = []
    for clf_name in classifier_names:
        clf = get_classifier(clf_name, scale_pos_weight=scale_pos_weight)
        classifiers_list.append((clf_name, clf))

    if len(classifiers_list) == 1:
        direction_model = classifiers_list[0][1]
        timestamped_log(f"Using {classifier_names[0].upper()} Classifier for Direction...")
    else:
        direction_model = VotingClassifier(estimators=classifiers_list, voting="soft")
        timestamped_log(f"Using VotingClassifier ({'_'.join(classifier_names).upper()}) for Direction...")

    direction_model.fit(X_dir_train, y_dir_train)

    y_dir_pred = direction_model.predict(X_dir_test)
    timestamped_log("Direction Model Evaluation:\n" + classification_report(y_dir_test, y_dir_pred))

    # Save
    direction_model_filename = "direction_" + "_".join(classifier_names) + ".pkl"
    direction_model_save_path = os.path.join(os.path.dirname(get_daily_model_path("dummy")), direction_model_filename)
    joblib.dump(direction_model, direction_model_save_path)
    timestamped_log(f"Direction Model saved to {direction_model_save_path}")

def train_daily_model(classifier_names: List[str] = [XGBOOST], threshold_percent=DEFAULT_DAILY_STRONG_MOVE_THRESHOLD):
    """
    Train classifiers for predicting strong movers and direction.
    """

    session: Session = SessionLocal()

    # Load features and close prices
    timestamped_log("Loading feature and close price data...")
    features = session.query(FeatureData).all()
    closes = session.query(EODData.trading_symbol, EODData.exchange, EODData.date, EODData.close).all()
    session.close()

    if not features or not closes:
        timestamped_log("No feature or close data found! Exiting...")
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
        "fo_eligible": f.fo_eligible
    } for f in features])

    closes_df = pd.DataFrame([{
        "trading_symbol": c.trading_symbol,
        "exchange": c.exchange,
        "date": c.date,
        "close": c.close
    } for c in closes])

    if features_df.empty or closes_df.empty:
        timestamped_log("Empty DataFrames after loading. Exiting...")
        return

    # Merge, sort, and create targets
    df = features_df.merge(closes_df, on=["trading_symbol", "exchange", "date"], how="left")
    df = df.sort_values(["trading_symbol", "date"]).reset_index(drop=True)

    df["next_close"] = df.groupby("trading_symbol")["close"].shift(-1)
    df["percent_move_next_day"] = ((df["next_close"] - df["close"]) / df["close"]) * 100
    df["strong_move_target"] = (df["percent_move_next_day"].abs() > threshold_percent).astype(int)
    df["direction_target"] = (df["percent_move_next_day"] > 0).astype(int)

    df = df.dropna(subset=["strong_move_target", "direction_target"])

    # Prepare feature set
    drop_cols = ["trading_symbol", "exchange", "date", "close", "next_close", "percent_move_next_day"]
    feature_cols = [col for col in df.columns if col not in drop_cols + ["strong_move_target", "direction_target"]]

    # --- Train Strong Move Model ---
    timestamped_log("Training Strong Move Model...")

    X = df[feature_cols]
    y = df["strong_move_target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y)

    num_positive = (y_train == 1).sum()
    num_negative = (y_train == 0).sum()
    scale_pos_weight = num_negative / max(num_positive, 1)

    classifiers_list = []
    for clf_name in classifier_names:
        clf = get_classifier(clf_name, scale_pos_weight=scale_pos_weight)
        classifiers_list.append((clf_name, clf))

    if len(classifiers_list) == 1:
        model = classifiers_list[0][1]
        timestamped_log(f"Using {classifier_names[0].upper()} Classifier...")
    else:
        model = VotingClassifier(estimators=classifiers_list, voting="soft")
        timestamped_log(f"Using VotingClassifier ({'_'.join(classifier_names).upper()})...")

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    timestamped_log("Strong Move Model Evaluation:\n" + classification_report(y_test, y_pred))

    # Feature importance
    if hasattr(model, "feature_importances_"):
        importance_df = pd.DataFrame({
            "feature": X_train.columns,
            "importance": model.feature_importances_
        }).sort_values(by="importance", ascending=False)
        timestamped_log("Feature Importances:\n" + importance_df.to_string(index=False))
    else:
        timestamped_log("Model does not support feature_importances_ attribute.")

    # Save Strong Move Model
    move_model_filename = "move_" + "_".join(classifier_names) + ".pkl"
    move_model_save_path = os.path.join(os.path.dirname(get_daily_model_path("dummy")), move_model_filename)
    joblib.dump(model, move_model_save_path)
    timestamped_log(f"Strong Move Model saved to {move_model_save_path}")

    # --- Train Direction Model ---
    train_direction_model(df, feature_cols, classifier_names)

if __name__ == "__main__":
    train_daily_model(classifier_names=[RANDOM_FOREST])
