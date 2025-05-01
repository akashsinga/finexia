# core/train/symbol_trainer.py

import joblib
import pandas as pd
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models.feature_data import FeatureData
from db.models.eod_data import EODData
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report
from sklearn.ensemble import VotingClassifier
from core.config import DEFAULT_DAILY_STRONG_MOVE_THRESHOLD, RANDOM_SEED
from core.train.model_selector import get_classifier, get_model_path

def timestamped_log(msg): print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def train_symbol_model(symbol: str, move_classifiers: List[str], direction_classifiers: List[str], threshold_percent: float = DEFAULT_DAILY_STRONG_MOVE_THRESHOLD, min_days: int = 1, max_days: int = 10):
    session: Session = SessionLocal()
    try:
        timestamped_log(f"Loading data for {symbol}...")
        features = session.query(FeatureData).filter(FeatureData.trading_symbol == symbol).all()
        closes = session.query(EODData.trading_symbol, EODData.exchange, EODData.date, EODData.close).filter(EODData.trading_symbol == symbol).all()

        if not features or not closes:
            timestamped_log(f"⚠️ No data for {symbol}. Skipping.")
            return

        features_df = pd.DataFrame([{col.name: getattr(f, col.name) for col in FeatureData.__table__.columns if col.name != 'id'} for f in features])
        closes_df = pd.DataFrame([{"trading_symbol": c.trading_symbol, "exchange": c.exchange, "date": c.date, "close": c.close} for c in closes])

        df = features_df.merge(closes_df, on=["trading_symbol", "exchange", "date"], how="left").sort_values("date").reset_index(drop=True)

        df["max_close_window"] = df["close"].shift(-min_days).rolling(max_days - min_days + 1, min_periods=1).max()
        df["min_close_window"] = df["close"].shift(-min_days).rolling(max_days - min_days + 1, min_periods=1).min()
        df["percent_up_move"] = ((df["max_close_window"] - df["close"]) / df["close"]) * 100
        df["percent_down_move"] = ((df["min_close_window"] - df["close"]) / df["close"]) * 100

        df["strong_move_target"] = ((df["percent_up_move"] >= threshold_percent) | (df["percent_down_move"].abs() >= threshold_percent)).astype(int)
        df["direction_target"] = (df["percent_up_move"] > df["percent_down_move"].abs()).astype(int)
        df = df.dropna(subset=["strong_move_target", "direction_target"])

        if df["strong_move_target"].sum() < 10:
            timestamped_log(f"⚠️ Not enough strong movers for {symbol}. Skipping.")
            return

        drop_cols = ["trading_symbol", "exchange", "date", "close", "max_close_window", "min_close_window", "percent_up_move", "percent_down_move"]
        feature_cols = [col for col in df.columns if col not in drop_cols + ["strong_move_target", "direction_target"]]

        X, y = df[feature_cols], df["strong_move_target"]
        tscv = TimeSeriesSplit(n_splits=5)
        train_idx, test_idx = list(tscv.split(X))[-1]
        X_train, X_test, y_train, y_test = X.iloc[train_idx], X.iloc[test_idx], y.iloc[train_idx], y.iloc[test_idx]
        scale_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1) * 3.0

        move_models = [(name, get_classifier(name, RANDOM_SEED, scale_weight)) for name in move_classifiers]
        move_model = move_models[0][1] if len(move_models) == 1 else VotingClassifier(estimators=move_models, voting="soft")
        move_model.fit(X_train, y_train)
        timestamped_log(f"✅ Move Model for {symbol}\n" + classification_report(y_test, move_model.predict(X_test)))
        joblib.dump(move_model, get_model_path(symbol, "move"))

        df_dir = df[df["strong_move_target"] == 1]
        if len(df_dir) < 10:
            timestamped_log(f"⚠️ Not enough direction data for {symbol}. Skipping direction model.")
            return

        Xd, yd = df_dir[feature_cols], df_dir["direction_target"]
        train_idx, test_idx = list(tscv.split(Xd))[-1]
        Xd_train, Xd_test, yd_train, yd_test = Xd.iloc[train_idx], Xd.iloc[test_idx], yd.iloc[train_idx], yd.iloc[test_idx]
        scale_dir = (yd_train == 0).sum() / max((yd_train == 1).sum(), 1) * 1.5

        dir_models = [(name, get_classifier(name, RANDOM_SEED, scale_dir)) for name in direction_classifiers]
        dir_model = dir_models[0][1] if len(dir_models) == 1 else VotingClassifier(estimators=dir_models, voting="soft")
        dir_model.fit(Xd_train, yd_train)
        timestamped_log(f"✅ Direction Model for {symbol}\n" + classification_report(yd_test, dir_model.predict(Xd_test)))
        joblib.dump(dir_model, get_model_path(symbol, "direction"))

    except Exception as e:
        timestamped_log(f"[ERROR] {symbol} training failed: {e}")
        session.rollback()
    finally:
        session.close()
