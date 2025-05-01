# core/train/daily_trainer.py

import os
import pandas as pd
import joblib
from datetime import datetime
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.database import SessionLocal
from db.models.feature_data import FeatureData
from db.models.eod_data import EODData
from db.models.symbol import Symbol
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from core.config import (RANDOM_FOREST, XGBOOST, LIGHTGBM, DAILY_MODELS_DIR,  DEFAULT_DAILY_STRONG_MOVE_THRESHOLD, RANDOM_FOREST_N_ESTIMATORS,  RANDOM_FOREST_MAX_DEPTH, RANDOM_SEED, RANDOM_FOREST_MIN_SAMPLES, RANDOM_FOREST_CLASS_WEIGHT, LIGHTGBM_N_ESTIMATORS, LIGHTGBM_LEARNING_RATE, LIGHTGBM_MAX_DEPTH, LIGHTGBM_MIN_CHILD_WEIGHT)

def timestamped_log(message: str): 
    """Log message with timestamp."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {message}")

def get_db_session() -> Session:
    """Creates and returns a database session."""
    return SessionLocal()

def get_classifier(classifier_name: str, scale_pos_weight: float = 1.0):
    """Factory function to create classifier instances with error handling."""
    try:
        if classifier_name == RANDOM_FOREST:
            return RandomForestClassifier(
                n_estimators=RANDOM_FOREST_N_ESTIMATORS, 
                max_depth=RANDOM_FOREST_MAX_DEPTH, 
                min_samples_split=RANDOM_FOREST_MIN_SAMPLES, 
                random_state=RANDOM_SEED, 
                class_weight=RANDOM_FOREST_CLASS_WEIGHT,
                n_jobs=-1  # Use all available cores
            )
        elif classifier_name == XGBOOST:
            from xgboost import XGBClassifier
            return XGBClassifier(
                n_estimators=300, 
                max_depth=6, 
                learning_rate=0.05, 
                min_child_weight=3, 
                random_state=RANDOM_SEED, 
                verbosity=0, 
                scale_pos_weight=scale_pos_weight,
                n_jobs=-1  # Use all available cores
            )
        elif classifier_name == LIGHTGBM:
            from lightgbm import LGBMClassifier
            return LGBMClassifier(
                n_estimators=LIGHTGBM_N_ESTIMATORS, 
                max_depth=LIGHTGBM_MAX_DEPTH, 
                learning_rate=LIGHTGBM_LEARNING_RATE, 
                min_child_weight=LIGHTGBM_MIN_CHILD_WEIGHT, 
                random_state=RANDOM_SEED, 
                verbosity=-1,
                n_jobs=-1  # Use all available cores
            )
        else:
            raise ValueError(f"Unsupported classifier: {classifier_name}")
    except ImportError as e:
        timestamped_log(f"[ERROR] Required library not available: {e}")
        raise

def get_model_path(symbol: str, model_type: str) -> str:
    """Generate model path with validation."""
    path = os.path.join(DAILY_MODELS_DIR, f"{symbol}_{model_type}.pkl")
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    return path

def load_symbol_data(session: Session, symbol: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load feature and price data for a symbol with error handling."""
    try:
        # Fetch feature data
        features = session.query(FeatureData).filter(FeatureData.trading_symbol == symbol).all()
        
        # Fetch closing prices
        closes = session.query(
            EODData.trading_symbol, 
            EODData.exchange, 
            EODData.date, 
            EODData.close
        ).filter(EODData.trading_symbol == symbol).all()
        
        # Convert to dataframes
        features_df = pd.DataFrame([
            {col.name: getattr(f, col.name) for col in FeatureData.__table__.columns if col.name != 'id'} 
            for f in features
        ]).copy()
        
        closes_df = pd.DataFrame([
            {
                "trading_symbol": c.trading_symbol,
                "exchange": c.exchange,
                "date": c.date,
                "close": c.close
            } 
            for c in closes
        ]).copy()
        
        return features_df, closes_df
    
    except SQLAlchemyError as e:
        timestamped_log(f"[ERROR] Database error loading data for {symbol}: {e}")
        return pd.DataFrame(), pd.DataFrame()

def prepare_training_data(features_df: pd.DataFrame, closes_df: pd.DataFrame, threshold_percent: float) -> Tuple[pd.DataFrame, List[str]]:
    """Prepare data for model training with forward-looking targets."""
    if features_df.empty or closes_df.empty:
        return pd.DataFrame(), []
        
    # Merge features with close prices
    df = features_df.merge(closes_df, on=["trading_symbol", "exchange", "date"], how="left")
    df = df.sort_values("date").reset_index(drop=True)
    
    # Calculate forward-looking metrics for target creation
    df["max_close_10d"] = df["close"].shift(-1).rolling(10, min_periods=1).max()
    df["min_close_10d"] = df["close"].shift(-1).rolling(10, min_periods=1).min()
    df["percent_up_move_10d"] = ((df["max_close_10d"] - df["close"]) / df["close"]) * 100
    df["percent_down_move_10d"] = ((df["min_close_10d"] - df["close"]) / df["close"]) * 100
    
    # Create binary target variables
    df["strong_move_target"] = ((df["percent_up_move_10d"] >= threshold_percent) | (df["percent_down_move_10d"].abs() >= threshold_percent)).astype(int)
    df["direction_target"] = (df["percent_up_move_10d"] > df["percent_down_move_10d"].abs()).astype(int)
    
    # Drop rows with missing targets
    df = df.dropna(subset=["strong_move_target", "direction_target"])
    
    # Define columns to exclude from feature set
    drop_cols = ["trading_symbol", "exchange", "date", "close", "max_close_10d", 
                "min_close_10d", "percent_up_move_10d", "percent_down_move_10d"]
    
    # Create feature list
    feature_cols = [col for col in df.columns if col not in drop_cols + ["strong_move_target", "direction_target"]]
    
    return df, feature_cols

def evaluate_model(model, X_test, y_test) -> Dict[str, float]:
    """Evaluate model performance and return metrics."""
    y_pred = model.predict(X_test)
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0)
    }
    
    if hasattr(model, "classes_") and len(model.classes_) > 1:
        probs = model.predict_proba(X_test)[:, 1]
        metrics["avg_confidence"] = probs.mean()
    
    return metrics

def train_models_for_one_symbol(
    symbol: str, 
    move_classifiers: List[str], 
    direction_classifiers: List[str], 
    threshold_percent: float = DEFAULT_DAILY_STRONG_MOVE_THRESHOLD
):
    """Train models for a single symbol with comprehensive error handling and logging."""
    session = get_db_session()
    start_time = datetime.now()
    
    try:
        timestamped_log(f"⏳ Loading data for {symbol}...")
        features_df, closes_df = load_symbol_data(session, symbol)
        
        if features_df.empty or closes_df.empty:
            timestamped_log(f"⚠️ No data found for {symbol}. Skipping.")
            return
            
        timestamped_log(f"📊 Preparing training data for {symbol}...")
        df, feature_cols = prepare_training_data(
            features_df, closes_df, threshold_percent
        )
        
        if df.empty or len(feature_cols) == 0:
            timestamped_log(f"⚠️ Failed to prepare training data for {symbol}. Skipping.")
            return
            
        move_positives = df["strong_move_target"].sum()
        if move_positives < 10:
            timestamped_log(f"⚠️ Not enough strong movers for {symbol} ({move_positives}). Skipping.")
            return
            
        timestamped_log(f"🧮 Features: {len(feature_cols)}, Samples: {len(df)}, "f"Positive examples: {move_positives} ({move_positives/len(df)*100:.1f}%)")
        
        # --------------- Train Move Model ---------------
        X, y = df[feature_cols], df["strong_move_target"]
        
        # Create time series cross-validation splits
        tscv = TimeSeriesSplit(n_splits=5)
        splits = list(tscv.split(X))
        train_idx, test_idx = splits[-1]  # Use the last split
        
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        # Calculate class weight for handling imbalance
        scale_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1) * 3.0
        
        # Create and train model
        timestamped_log(f"🏋️ Training Move Model for {symbol} with {','.join(move_classifiers)}...")
        move_estimators = [
            (clf_name, get_classifier(clf_name, scale_pos_weight=scale_weight)) 
            for clf_name in move_classifiers
        ]
        
        move_model = move_estimators[0][1] if len(move_estimators) == 1 else VotingClassifier(
            estimators=move_estimators, voting="soft"
        )
        
        # Train with timing
        train_start = datetime.now()
        move_model.fit(X_train, y_train)
        train_time = (datetime.now() - train_start).total_seconds()
        
        # Evaluate
        metrics = evaluate_model(move_model, X_test, y_test)
        
        timestamped_log(f"✅ Move Model for {symbol} trained in {train_time:.1f}s:")
        timestamped_log(f"   Accuracy: {metrics['accuracy']:.3f}, Precision: {metrics['precision']:.3f}, "f"Recall: {metrics['recall']:.3f}, F1: {metrics['f1']:.3f}")
        
        # Save model
        joblib.dump(move_model, get_model_path(symbol, "move"))
        
        # --------------- Train Direction Model ---------------
        # Only train direction model for strong moves
        df_dir = df[df["strong_move_target"] == 1]
        if len(df_dir) < 10:
            timestamped_log(f"⚠️ Not enough direction data for {symbol}. Skipping direction model.")
            return
            
        X_dir, y_dir = df_dir[feature_cols], df_dir["direction_target"]
        
        # Create train/test split for direction model
        dir_tscv = TimeSeriesSplit(n_splits=5)
        dir_splits = list(dir_tscv.split(X_dir))
        if not dir_splits:
            timestamped_log(f"⚠️ Cannot create time series split for {symbol} direction model. Skipping.")
            return
            
        dir_train_idx, dir_test_idx = dir_splits[-1]
        
        Xd_train, Xd_test = X_dir.iloc[dir_train_idx], X_dir.iloc[dir_test_idx]
        yd_train, yd_test = y_dir.iloc[dir_train_idx], y_dir.iloc[dir_test_idx]
        
        # Check if we have enough samples
        if len(Xd_train) < 5 or len(Xd_test) < 5:
            timestamped_log(f"⚠️ Not enough train/test samples for {symbol} direction model. Skipping.")
            return
            
        # Calculate class weight
        scale_dir = (yd_train == 0).sum() / max((yd_train == 1).sum(), 1) * 1.5
        
        # Create and train model
        timestamped_log(f"🏋️ Training Direction Model for {symbol} with {','.join(direction_classifiers)}...")
        direction_estimators = [
            (clf_name, get_classifier(clf_name, scale_pos_weight=scale_dir)) 
            for clf_name in direction_classifiers
        ]
        
        direction_model = direction_estimators[0][1] if len(direction_estimators) == 1 else VotingClassifier(
            estimators=direction_estimators, voting="soft"
        )
        
        # Train with timing
        dir_train_start = datetime.now()
        direction_model.fit(Xd_train, yd_train)
        dir_train_time = (datetime.now() - dir_train_start).total_seconds()
        
        # Evaluate
        dir_metrics = evaluate_model(direction_model, Xd_test, yd_test)
        
        timestamped_log(f"✅ Direction Model for {symbol} trained in {dir_train_time:.1f}s:")
        timestamped_log(f"   Accuracy: {dir_metrics['accuracy']:.3f}, Precision: {dir_metrics['precision']:.3f}, "f"Recall: {dir_metrics['recall']:.3f}, F1: {dir_metrics['f1']:.3f}")
        
        # Save model
        joblib.dump(direction_model, get_model_path(symbol, "direction"))
        
        total_time = (datetime.now() - start_time).total_seconds()
        timestamped_log(f"⌛ Total training time for {symbol}: {total_time:.1f}s")

    except Exception as e:
        timestamped_log(f"[ERROR] Exception during training for {symbol}: {str(e)}")
    finally:
        session.close()

def train_daily_model(
    move_classifiers: List[str] = [RANDOM_FOREST], 
    direction_classifiers: List[str] = [RANDOM_FOREST], 
    threshold_percent: float = DEFAULT_DAILY_STRONG_MOVE_THRESHOLD
):
    """Run training for all active symbols with progress tracking."""
    session = get_db_session()
    total_start_time = datetime.now()
    completed, failed = 0, 0
    
    try:
        # Get all active symbols
        symbols = session.query(Symbol.trading_symbol).filter(Symbol.active == True).all()
        if not symbols:
            timestamped_log("No active symbols found. Exiting...")
            return

        total_symbols = len(symbols)
        timestamped_log(f"Found {total_symbols} active symbols. Starting training...")
        
        # Train models for each symbol
        for i, s in enumerate(symbols):
            symbol = s.trading_symbol
            
            try:
                timestamped_log(f"[{i+1}/{total_symbols}] Processing {symbol}...")
                train_models_for_one_symbol(
                    symbol=symbol,
                    move_classifiers=move_classifiers,
                    direction_classifiers=direction_classifiers,
                    threshold_percent=threshold_percent
                )
                completed += 1
            except Exception as e:
                timestamped_log(f"[ERROR] Symbol {symbol} training failed: {e}")
                failed += 1
                
            # Log progress
            if (i+1) % 10 == 0 or (i+1) == total_symbols:
                elapsed = (datetime.now() - total_start_time).total_seconds() / 60
                remaining = elapsed / (i+1) * (total_symbols - i - 1)
                timestamped_log(f"Progress: {i+1}/{total_symbols} symbols processed "
                              f"({completed} completed, {failed} failed). "
                              f"Elapsed: {elapsed:.1f}m, Est. Remaining: {remaining:.1f}m")

    except Exception as e:
        timestamped_log(f"[ERROR] Exception during daily model training: {e}")
    finally:
        session.close()
        total_time = (datetime.now() - total_start_time).total_seconds() / 60
        timestamped_log(f"Training completed in {total_time:.1f} minutes. "f"Successful: {completed}/{total_symbols} symbols.")

if __name__ == "__main__":
    train_daily_model(move_classifiers=[RANDOM_FOREST], direction_classifiers=[RANDOM_FOREST])
