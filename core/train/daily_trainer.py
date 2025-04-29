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
from db.models.symbol import Symbol
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from core.config import (RANDOM_FOREST, XGBOOST, LIGHTGBM, DAILY_MODELS_DIR, DEFAULT_DAILY_STRONG_MOVE_THRESHOLD, RANDOM_FOREST_N_ESTIMATORS, RANDOM_FOREST_MAX_DEPTH, RANDOM_SEED, RANDOM_FOREST_MIN_SAMPLES, RANDOM_FOREST_CLASS_WEIGHT, LIGHTGBM_N_ESTIMATORS, LIGHTGBM_LEARNING_RATE, LIGHTGBM_MAX_DEPTH, LIGHTGBM_MIN_CHILD_WEIGHT)

def timestamped_log(message: str): print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {message}")

def get_classifier(classifier_name: str, scale_pos_weight: float = 1.0):
    if classifier_name == RANDOM_FOREST:
        return RandomForestClassifier(n_estimators=RANDOM_FOREST_N_ESTIMATORS, max_depth=RANDOM_FOREST_MAX_DEPTH, min_samples_split=RANDOM_FOREST_MIN_SAMPLES, random_state=RANDOM_SEED, class_weight=RANDOM_FOREST_CLASS_WEIGHT)
    elif classifier_name == XGBOOST:
        from xgboost import XGBClassifier
        return XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.05, min_child_weight=3, random_state=RANDOM_SEED, verbosity=0, scale_pos_weight=scale_pos_weight)
    elif classifier_name == LIGHTGBM:
        from lightgbm import LGBMClassifier
        return LGBMClassifier(n_estimators=LIGHTGBM_N_ESTIMATORS, max_depth=LIGHTGBM_MAX_DEPTH, learning_rate=LIGHTGBM_LEARNING_RATE, min_child_weight=LIGHTGBM_MIN_CHILD_WEIGHT, random_state=RANDOM_SEED, verbosity=-1)
    else:
        raise ValueError(f"Unsupported classifier: {classifier_name}")

def get_model_path(symbol: str, model_type: str): return os.path.join(DAILY_MODELS_DIR, f"{symbol}_{model_type}.pkl")

def train_models_for_one_symbol(symbol: str, move_classifiers: List[str], direction_classifiers: List[str], threshold_percent: float = DEFAULT_DAILY_STRONG_MOVE_THRESHOLD):
    session: Session = SessionLocal()
    try:
        timestamped_log(f"⏳ Loading data for {symbol}...")
        features = session.query(FeatureData).filter(FeatureData.trading_symbol == symbol).all()
        closes = session.query(EODData.trading_symbol, EODData.exchange, EODData.date, EODData.close).filter(EODData.trading_symbol == symbol).all()

        if not features or not closes:
            timestamped_log(f"⚠️ No data found for {symbol}. Skipping.")
            return

        features_df = pd.DataFrame([{col.name: getattr(f, col.name) for col in FeatureData.__table__.columns if col.name != 'id'} for f in features]).copy()
        closes_df = pd.DataFrame([{
            "trading_symbol": c.trading_symbol,
            "exchange": c.exchange,
            "date": c.date,
            "close": c.close
        } for c in closes]).copy()

        df = features_df.merge(closes_df, on=["trading_symbol", "exchange", "date"], how="left")
        df = df.sort_values("date").reset_index(drop=True)

        df["max_close_10d"] = df["close"].shift(-1).rolling(10, min_periods=1).max()
        df["min_close_10d"] = df["close"].shift(-1).rolling(10, min_periods=1).min()
        df["percent_up_move_10d"] = ((df["max_close_10d"] - df["close"]) / df["close"]) * 100
        df["percent_down_move_10d"] = ((df["min_close_10d"] - df["close"]) / df["close"]) * 100
        df["strong_move_target"] = ((df["percent_up_move_10d"] >= threshold_percent) | (df["percent_down_move_10d"].abs() >= threshold_percent)).astype(int)
        df["direction_target"] = (df["percent_up_move_10d"] > df["percent_down_move_10d"].abs()).astype(int)
        df = df.dropna(subset=["strong_move_target", "direction_target"])

        if df["strong_move_target"].sum() < 10:
            timestamped_log(f"⚠️ Not enough strong movers for {symbol}. Skipping.")
            return

        drop_cols = ["trading_symbol", "exchange", "date", "close", "max_close_10d", "min_close_10d", "percent_up_move_10d", "percent_down_move_10d"]
        feature_cols = [col for col in df.columns if col not in drop_cols + ["strong_move_target", "direction_target"]]

        # Train Move Model
        X, y = df[feature_cols], df["strong_move_target"]
        tscv = TimeSeriesSplit(n_splits=5)
        train_idx, test_idx = list(tscv.split(X))[-1]
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        scale_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1) * 3.0

        move_estimators = [(clf_name, get_classifier(clf_name, scale_pos_weight=scale_weight)) for clf_name in move_classifiers]
        move_model = move_estimators[0][1] if len(move_estimators) == 1 else VotingClassifier(estimators=move_estimators, voting="soft")
        move_model.fit(X_train, y_train)
        timestamped_log(f"✅ Trained Move Model for {symbol}\n" + classification_report(y_test, move_model.predict(X_test)))
        joblib.dump(move_model, get_model_path(symbol, "move"))

        # Train Direction Model
        df_dir = df[df["strong_move_target"] == 1]
        if len(df_dir) < 10:
            timestamped_log(f"⚠️ Not enough direction data for {symbol}. Skipping direction model.")
            return

        X_dir, y_dir = df_dir[feature_cols], df_dir["direction_target"]
        train_idx, test_idx = list(tscv.split(X_dir))[-1]
        Xd_train, Xd_test = X_dir.iloc[train_idx], X_dir.iloc[test_idx]
        yd_train, yd_test = y_dir.iloc[train_idx], y_dir.iloc[test_idx]
        scale_dir = (yd_train == 0).sum() / max((yd_train == 1).sum(), 1) * 1.5

        direction_estimators = [(clf_name, get_classifier(clf_name, scale_pos_weight=scale_dir)) for clf_name in direction_classifiers]
        direction_model = direction_estimators[0][1] if len(direction_estimators) == 1 else VotingClassifier(estimators=direction_estimators, voting="soft")
        direction_model.fit(Xd_train, yd_train)
        timestamped_log(f"✅ Trained Direction Model for {symbol}\n" + classification_report(yd_test, direction_model.predict(Xd_test)))
        joblib.dump(direction_model, get_model_path(symbol, "direction"))

    except Exception as e:
        timestamped_log(f"[ERROR] Exception during training for {symbol}: {e}")
    finally:
        session.close()

def train_daily_model(move_classifiers: List[str] = [RANDOM_FOREST], direction_classifiers: List[str] = [RANDOM_FOREST], threshold_percent: float = DEFAULT_DAILY_STRONG_MOVE_THRESHOLD):
    session: Session = SessionLocal()
    try:
        symbols = session.query(Symbol.trading_symbol).filter(Symbol.active == True).all()
        if not symbols:
            timestamped_log("No active symbols found. Exiting...")
            return

        timestamped_log(f"Found {len(symbols)} active symbols. Starting training...")
        for s in symbols:
            train_models_for_one_symbol(symbol=s.trading_symbol, move_classifiers=move_classifiers, direction_classifiers=direction_classifiers, threshold_percent=threshold_percent)

    except Exception as e:
        timestamped_log(f"[ERROR] Exception during daily model training: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    train_daily_model(move_classifiers=[RANDOM_FOREST], direction_classifiers=[RANDOM_FOREST])
