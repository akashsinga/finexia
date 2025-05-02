# core/train/daily_trainer.py

import os
import pandas as pd
import numpy as np
import joblib
import json
import gc
from datetime import datetime
from typing import List, Dict, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.database import SessionLocal
from db.models.symbol import Symbol
from db.models.model_performance import ModelPerformance
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.ensemble import RandomForestClassifier
from functools import partial
from core.config import (RANDOM_FOREST, XGBOOST, LIGHTGBM, DAILY_MODELS_DIR, DEFAULT_DAILY_STRONG_MOVE_THRESHOLD, RANDOM_FOREST_N_ESTIMATORS, RANDOM_FOREST_MAX_DEPTH, RANDOM_SEED, RANDOM_FOREST_MIN_SAMPLES, RANDOM_FOREST_CLASS_WEIGHT, LIGHTGBM_N_ESTIMATORS,LIGHTGBM_LEARNING_RATE, LIGHTGBM_MAX_DEPTH, LIGHTGBM_MIN_CHILD_WEIGHT)

# Monkeypatch to completely disable CPU core detection warning
os.environ["LOKY_MAX_CPU_COUNT"] = str(os.cpu_count())

# Completely disable the problematic function
import joblib.externals.loky.backend.context as loky_context

# Replace the problematic function with a simple version
def _fixed_count_physical_cores():
    return os.cpu_count()

# Apply the monkeypatch
loky_context._count_physical_cores = _fixed_count_physical_cores

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
            return RandomForestClassifier(n_estimators=min(RANDOM_FOREST_N_ESTIMATORS, 100), max_depth=RANDOM_FOREST_MAX_DEPTH, min_samples_split=RANDOM_FOREST_MIN_SAMPLES, random_state=RANDOM_SEED, class_weight=RANDOM_FOREST_CLASS_WEIGHT, n_jobs=1)
        elif classifier_name == XGBOOST:
            from xgboost import XGBClassifier
            return XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, min_child_weight=3, random_state=RANDOM_SEED, verbosity=0, scale_pos_weight=scale_pos_weight, n_jobs=1, tree_method='hist')
        elif classifier_name == LIGHTGBM:
            from lightgbm import LGBMClassifier
            return LGBMClassifier(n_estimators=min(LIGHTGBM_N_ESTIMATORS, 100), max_depth=LIGHTGBM_MAX_DEPTH, learning_rate=LIGHTGBM_LEARNING_RATE * 2, min_child_weight=LIGHTGBM_MIN_CHILD_WEIGHT, random_state=RANDOM_SEED, verbosity=-1, n_jobs=1)
        else:
            raise ValueError(f"Unsupported classifier: {classifier_name}")
    except ImportError as e:
        timestamped_log(f"[ERROR] Required library not available: {e}")
        raise

def get_model_path(symbol: str, model_type: str) -> str:
    """Generate model path with validation."""
    path = os.path.join(DAILY_MODELS_DIR, f"{symbol}_{model_type}.pkl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

def load_symbol_data(symbol: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load feature and price data for a symbol with error handling."""
    session = get_db_session()
    try:
        # Use direct parameterized SQL with correct parameter format
        features_query = """
            SELECT * FROM features_data 
            WHERE trading_symbol = %(symbol)s
            ORDER BY date
        """
        closes_query = """
            SELECT trading_symbol, exchange, date, close 
            FROM eod_data 
            WHERE trading_symbol = %(symbol)s
            ORDER BY date
        """
        features_df = pd.read_sql_query(features_query, session.bind, params={"symbol": symbol})
        closes_df = pd.read_sql_query(closes_query, session.bind, params={"symbol": symbol})
        return features_df, closes_df
    
    except SQLAlchemyError as e:
        timestamped_log(f"[ERROR] Database error loading data for {symbol}: {e}")
        return pd.DataFrame(), pd.DataFrame()
    finally:
        session.close()

def clean_data_for_model(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataframe by handling non-numeric columns, infinities, and outliers."""
    clean_df = df.copy()
    exclude_cols = ['id', 'trading_symbol', 'exchange', 'date', 'created_at', 'updated_at', 'source_tag']
    feature_cols = [col for col in clean_df.columns if col not in exclude_cols]
    numeric_df = clean_df[feature_cols].select_dtypes(include=['number']).copy()
    
    # Fast vectorized operations for data cleaning
    numeric_df = numeric_df.replace([np.inf, -np.inf], np.nan)
    
    # Calculate means for NaN filling
    column_means = numeric_df.mean().fillna(0)
    numeric_df = numeric_df.fillna(column_means)
    
    # Use percentile-based clipping for outliers
    for col in numeric_df.columns:
        if numeric_df[col].count() > 10:  # Only process columns with enough data
            q_low, q_high = numeric_df[col].quantile([0.01, 0.99])
            numeric_df[col] = numeric_df[col].clip(q_low, q_high)
    
    return numeric_df

def select_best_features(X: pd.DataFrame, y: pd.Series, n_features: int = 8) -> List[str]:
    """Select most important features using LightGBM."""
    X_clean = clean_data_for_model(X)
    if X_clean.shape[1] <= n_features:
        return X_clean.columns.tolist()
        
    try:
        from lightgbm import LGBMClassifier
        # Use a lightweight model just for feature importance
        model = LGBMClassifier(
            n_estimators=50,  # Reduced from 100 for speed
            importance_type='gain',
            verbosity=-1,
            random_state=RANDOM_SEED
        )
        model.fit(X_clean, y)
        
        # Get feature importances
        importances = pd.DataFrame({'feature': X_clean.columns, 'importance': model.feature_importances_}).sort_values('importance', ascending=False)
        
        # Return top n features
        top_features = importances.head(n_features)['feature'].tolist()
        timestamped_log(f"🔍 Selected top features: {', '.join(top_features)}")
        return top_features
    except:
        timestamped_log(f"[WARNING] Feature selection failed, using all {X_clean.shape[1]} features.")
        return X_clean.columns.tolist()

def prepare_training_data(features_df: pd.DataFrame, closes_df: pd.DataFrame, threshold_percent: float, min_days: int = 1, max_days: int = 10) -> Tuple[pd.DataFrame, List[str]]:
    """Prepare data for model training with forward-looking targets and adaptive timeframes."""
    if features_df.empty or closes_df.empty:
        return pd.DataFrame(), []
        
    # Convert date column to datetime
    features_df['date'] = pd.to_datetime(features_df['date'])
    closes_df['date'] = pd.to_datetime(closes_df['date'])
    
    # Merge features with close prices - use inner merge for speed
    df = features_df.merge(closes_df, on=["trading_symbol", "exchange", "date"], how="inner").sort_values("date").reset_index(drop=True)
    
    # Calculate dynamic lookback window - simplified for speed
    if 'atr_14_normalized' in df.columns:
        # Calculate volatility and scale to prediction window range
        volatility = df['atr_14_normalized'].replace([np.inf, -np.inf], np.nan).rolling(20).mean().fillna(0.02)
        volatility_scaled = min_days + (max_days - min_days) * (1 - np.clip((volatility - volatility.min()) / (volatility.max() - volatility.min() + 1e-10), 0, 1))
        df['prediction_window'] = np.clip(np.round(volatility_scaled), min_days, max_days)
    else:
        # Fallback to fixed window
        df['prediction_window'] = max_days
    
    # Using a simpler approach to avoid date sorting issues
    # Get all symbols in the DataFrame
    symbols = df['trading_symbol'].unique()
    
    # Process each symbol separately
    for symbol in symbols:
        symbol_mask = df['trading_symbol'] == symbol
        symbol_df = df[symbol_mask].copy()
        
        # Calculate future max and min prices for each row
        dates = symbol_df['date'].tolist()
        closes = symbol_df['close'].tolist()
        windows = symbol_df['prediction_window'].astype(int).tolist()
        
        max_future_prices = []
        min_future_prices = []
        
        # For each date in the sorted sequence
        for i in range(len(dates)):
            current_date = dates[i]
            window = windows[i]
            
            # Find future prices within the window
            future_prices = []
            for j in range(i + 1, len(dates)):
                if (dates[j] - current_date).days <= window:
                    future_prices.append(closes[j])
                elif (dates[j] - current_date).days > window:
                    break
            
            if future_prices:
                max_future_prices.append(max(future_prices))
                min_future_prices.append(min(future_prices))
            else:
                max_future_prices.append(np.nan)
                min_future_prices.append(np.nan)
        
        # Assign back to the main DataFrame
        df.loc[symbol_mask, 'max_close_future'] = max_future_prices
        df.loc[symbol_mask, 'min_close_future'] = min_future_prices
    
    # Calculate percentage moves, handling zeros and NaNs
    close_nonzero = df["close"].replace(0, np.nan)
    df["percent_up_move"] = ((df["max_close_future"] - df["close"]) / close_nonzero) * 100
    df["percent_down_move"] = ((df["min_close_future"] - df["close"]) / close_nonzero) * 100
    
    # Create binary target variables
    df["strong_move_target"] = ((df["percent_up_move"] >= threshold_percent) | (df["percent_down_move"].abs() >= threshold_percent)).astype(int)
    df["direction_target"] = (df["percent_up_move"] > df["percent_down_move"].abs()).astype(int)
    
    # Drop rows with missing targets
    df = df.dropna(subset=["strong_move_target", "direction_target"])
    
    # Define columns to exclude from feature set
    drop_cols = ["id", "trading_symbol", "exchange", "date", "close", "max_close_future", 
                "min_close_future", "percent_up_move", "percent_down_move", 
                "prediction_window", "created_at", "updated_at", "source_tag"]
    
    # Create feature list
    feature_cols = [col for col in df.columns if col not in drop_cols + ["strong_move_target", "direction_target"]]
    
    return df, feature_cols

def evaluate_model(model, X_test, y_test) -> Dict[str, float]:
    """Evaluate model performance and return metrics."""
    y_pred = model.predict(X_test)
    
    metrics = {"accuracy": accuracy_score(y_test, y_pred), "precision": precision_score(y_test, y_pred, zero_division=0), "recall": recall_score(y_test, y_pred, zero_division=0), "f1": f1_score(y_test, y_pred, zero_division=0)}
    
    if hasattr(model, "predict_proba") and hasattr(model, "classes_") and len(model.classes_) > 1:
        try:
            metrics["avg_confidence"] = model.predict_proba(X_test)[:, 1].mean()
        except:
            pass
    
    return metrics

def save_model_performance(session: Session, symbol: str, model_type: str, metrics: Dict, selected_features: List[str], threshold: float) -> bool:
    """Save model performance metrics to database."""
    try:
        # Check if we already have a record for today
        existing = session.query(ModelPerformance).filter(ModelPerformance.trading_symbol == symbol,ModelPerformance.model_type == model_type,ModelPerformance.evaluation_date == datetime.now().date()).first()
        
        if existing:
            # Update existing record
            performance = existing
        else:
            # Create new record
            performance = ModelPerformance(
                trading_symbol=symbol,
                model_type=model_type,
                training_date=datetime.now().date(),
                evaluation_date=datetime.now().date()
            )
        
        # Update metrics
        performance.accuracy = metrics.get("accuracy", 0)
        performance.precision = metrics.get("precision", 0)
        performance.recall = metrics.get("recall", 0)
        performance.f1_score = metrics.get("f1", 0)
        performance.sensitivity_threshold = threshold
        performance.effective_features = json.dumps(selected_features)
        
        # Set prediction counts (these were missing before)
        performance.predictions_count = len(metrics.get("y_test", [])) if "y_test" in metrics else 100  # Default value
        performance.successful_count = int(metrics.get("accuracy", 0) * performance.predictions_count)
        
        session.add(performance)
        session.commit()  # Commit changes
        timestamped_log(f"📊 Saved {model_type} model performance metrics to database for {symbol} (Acc: {metrics.get('accuracy', 0):.3f}, F1: {metrics.get('f1', 0):.3f})")
        return True
    except Exception as e:
        session.rollback()  # Rollback in case of error
        timestamped_log(f"[WARNING] Failed to save performance for {symbol}: {e}")
        return False

def train_models_for_one_symbol(symbol: str, move_classifiers: List[str], direction_classifiers: List[str], threshold_percent: float = DEFAULT_DAILY_STRONG_MOVE_THRESHOLD,min_days: int = 1,max_days: int = 10) -> Dict[str, float]:
    """Train models for a single symbol with comprehensive error handling and logging."""
    start_time = datetime.now()
    results = {"symbol": symbol, "status": "failed", "move_metrics": {}, "direction_metrics": {}, "duration": 0, "error": None}
    
    try:
        timestamped_log(f"⏳ Loading data for {symbol}...")
        features_df, closes_df = load_symbol_data(symbol)
        
        if features_df.empty or closes_df.empty:
            timestamped_log(f"⚠️ No data found for {symbol}. Skipping.")
            results["error"] = "No data found"
            return results
            
        timestamped_log(f"📊 Preparing training data for {symbol}...")
        df, feature_cols = prepare_training_data(
            features_df, closes_df, threshold_percent, min_days, max_days
        )
        
        if df.empty or len(feature_cols) == 0:
            timestamped_log(f"⚠️ Failed to prepare training data for {symbol}. Skipping.")
            results["error"] = "Failed to prepare training data"
            return results
            
        move_positives = df["strong_move_target"].sum()
        if move_positives < 10:
            timestamped_log(f"⚠️ Not enough strong movers for {symbol} ({move_positives}). Skipping.")
            results["error"] = f"Not enough strong movers ({move_positives})"
            return results
            
        timestamped_log(f"🧮 Features: {len(feature_cols)}, Samples: {len(df)}, Positive examples: {move_positives} ({move_positives/len(df)*100:.1f}%)")
        
        # --------------- Train Move Model ---------------
        # Exclude non-numeric and date columns before selecting features
        X = df[feature_cols].copy()
        y = df["strong_move_target"].copy()
        
        # Select best features - reduced to 8 features for speed
        selected_features = select_best_features(X, y, n_features=8)
        
        # Clean data for modeling
        X_selected = clean_data_for_model(df[selected_features])
        
        # Instead of cross-validation, use a simple time-based train/test split
        # Approximately 80% for training, 20% for testing
        train_size = int(len(X_selected) * 0.8)
        train_idx = list(range(train_size))
        test_idx = list(range(train_size, len(X_selected)))
        
        X_train, X_test = X_selected.iloc[train_idx], X_selected.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        # Calculate class weight for handling imbalance
        pos_count = y_train.sum()
        neg_count = len(y_train) - pos_count
        scale_weight = neg_count / max(pos_count, 1) * 3.0
        
        # Create and train model - use only one model type for speed
        timestamped_log(f"🏋️ Training Move Model for {symbol} with {move_classifiers[0]}...")
        move_model = get_classifier(move_classifiers[0], scale_pos_weight=scale_weight)
        
        # Train with timing
        train_start = datetime.now()
        move_model.fit(X_train, y_train)
        train_time = (datetime.now() - train_start).total_seconds()
        
        # Evaluate
        metrics = evaluate_model(move_model, X_test, y_test)
        metrics["y_test"] = y_test  # Store for use in save_model_performance
        results["move_metrics"] = metrics
        
        timestamped_log(f"✅ Move Model for {symbol} trained in {train_time:.1f}s:")
        timestamped_log(f"   Accuracy: {metrics['accuracy']:.3f}, Precision: {metrics['precision']:.3f}, Recall: {metrics['recall']:.3f}, F1: {metrics['f1']:.3f}")
        
        # Save model and selected features
        model_data = {"model": move_model, "selected_features": selected_features, "metrics": metrics, "training_date": datetime.now().strftime("%Y-%m-%d"), "positive_samples": int(y_train.sum()), "total_samples": len(y_train)}
        joblib.dump(model_data, get_model_path(symbol, "move"))
        
        # Save performance metrics to database
        session = get_db_session()
        try:
            save_model_performance(session=session,symbol=symbol,model_type="move",metrics=metrics,selected_features=selected_features,threshold=threshold_percent)
        except Exception as e:
            timestamped_log(f"[ERROR] Failed to save model performance: {e}")
        
        # --------------- Train Direction Model ---------------
        # Only train direction model for strong moves
        df_dir = df[df["strong_move_target"] == 1]
        if len(df_dir) < 10:
            timestamped_log(f"⚠️ Not enough direction data for {symbol}. Skipping direction model.")
            results["error"] = "Not enough direction data"
            results["status"] = "partial_success"
            session.close()
            return results
            
        X_dir, y_dir = df_dir[feature_cols], df_dir["direction_target"]
        
        # Feature selection for direction model
        selected_dir_features = select_best_features(X_dir, y_dir, n_features=8)
        X_dir_selected = clean_data_for_model(df_dir[selected_dir_features])
        
        # Direction model - simple train/test split instead of cross-validation
        dir_train_size = int(len(X_dir_selected) * 0.8)
        dir_train_idx = list(range(dir_train_size))
        dir_test_idx = list(range(dir_train_size, len(X_dir_selected)))
        
        if len(dir_train_idx) < 5 or len(dir_test_idx) < 5:
            timestamped_log(f"⚠️ Not enough train/test samples for {symbol} direction model. Skipping.")
            results["error"] = "Not enough train/test samples for direction model"
            results["status"] = "partial_success"
            session.close()
            return results
            
        Xd_train, Xd_test = X_dir_selected.iloc[dir_train_idx], X_dir_selected.iloc[dir_test_idx]
        yd_train, yd_test = y_dir.iloc[dir_train_idx], y_dir.iloc[dir_test_idx]
        
        # Calculate class weight
        dir_pos_count = yd_train.sum()
        dir_neg_count = len(yd_train) - dir_pos_count
        scale_dir = dir_neg_count / max(dir_pos_count, 1) * 1.5
        
        # Create and train model - ONLY USE ONE MODEL
        timestamped_log(f"🏋️ Training Direction Model for {symbol} with {direction_classifiers[0]}...")
        direction_model = get_classifier(direction_classifiers[0], scale_pos_weight=scale_dir)
        
        # Train with timing
        dir_train_start = datetime.now()
        direction_model.fit(Xd_train, yd_train)
        dir_train_time = (datetime.now() - dir_train_start).total_seconds()
        
        # Evaluate
        dir_metrics = evaluate_model(direction_model, Xd_test, yd_test)
        dir_metrics["y_test"] = yd_test  # Store for use in save_model_performance
        results["direction_metrics"] = dir_metrics
        
        timestamped_log(f"✅ Direction Model for {symbol} trained in {dir_train_time:.1f}s:")
        timestamped_log(f"   Accuracy: {dir_metrics['accuracy']:.3f}, Precision: {dir_metrics['precision']:.3f}, Recall: {dir_metrics['recall']:.3f}, F1: {dir_metrics['f1']:.3f}")
        
        # Save model and selected features
        dir_model_data = {"model": direction_model, "selected_features": selected_dir_features, "metrics": dir_metrics, "training_date": datetime.now().strftime("%Y-%m-%d"), "positive_samples": int(yd_train.sum()), "total_samples": len(yd_train)}
        joblib.dump(dir_model_data, get_model_path(symbol, "direction"))
        
        # Save direction model performance
        save_model_performance(
            session=session,
            symbol=symbol,
            model_type="direction",
            metrics=dir_metrics,
            selected_features=selected_dir_features,
            threshold=threshold_percent
        )
        session.close()
        
        total_time = (datetime.now() - start_time).total_seconds()
        timestamped_log(f"⌛ Total training time for {symbol}: {total_time:.1f}s")
        
        results["status"] = "success"
        results["duration"] = total_time
        return results

    except Exception as e:
        total_time = (datetime.now() - start_time).total_seconds()
        timestamped_log(f"[ERROR] Exception during training for {symbol}: {str(e)}")
        results["status"] = "failed"
        results["error"] = str(e)
        results["duration"] = total_time
        return results

def train_symbol_wrapper(symbol: str, move_classifiers, direction_classifiers, threshold_percent, min_days, max_days):
    """Wrapper function for multiprocessing."""
    try:
        return train_models_for_one_symbol(symbol=symbol,move_classifiers=move_classifiers,direction_classifiers=direction_classifiers,threshold_percent=threshold_percent,min_days=min_days,max_days=max_days)
    except Exception as e:
        return {"symbol": symbol, "status": "error", "error": str(e), "move_metrics": {}, "direction_metrics": {}, "duration": 0}

def train_daily_model(move_classifiers: List[str] = [LIGHTGBM],direction_classifiers: List[str] = [LIGHTGBM],threshold_percent: float = DEFAULT_DAILY_STRONG_MOVE_THRESHOLD,min_days: int = 1,max_days: int = 10,max_workers: int = None):
    """Run training for all active symbols with improved parallelization and adaptive timeframes."""
    session = get_db_session()
    total_start_time = datetime.now()
    
    try:
        # Get all active symbols
        symbols = session.query(Symbol.trading_symbol).filter(Symbol.active == True).all()
        if not symbols:
            timestamped_log("No active symbols found. Exiting...")
            return

        symbol_list = [s.trading_symbol for s in symbols]
        total_symbols = len(symbol_list)
        
        # Determine optimal worker count if not specified
        if max_workers is None:
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            max_workers = max(1, min(cpu_count - 1, total_symbols, 8))  # Use at most 8 workers or CPU count-1
        
        timestamped_log(f"Found {total_symbols} active symbols. Starting training with {max_workers} workers...")
        timestamped_log(f"Using adaptive timeframes: {min_days}-{max_days} days")
        timestamped_log(f"Using model types: Move={move_classifiers}, Direction={direction_classifiers}")
        
        # Prepare partial function for multiprocessing
        train_fn = partial(train_symbol_wrapper,move_classifiers=move_classifiers,direction_classifiers=direction_classifiers,threshold_percent=threshold_percent,min_days=min_days,max_days=max_days)
        
        # Process symbols in batches for better memory management
        batch_size = 50  # Process 50 symbols at a time
        results = []
        
        for i in range(0, total_symbols, batch_size):
            batch_symbols = symbol_list[i:i+batch_size]
            timestamped_log(f"Processing batch {i//batch_size + 1}/{(total_symbols+batch_size-1)//batch_size} ({len(batch_symbols)} symbols)")
            
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(train_fn, symbol): symbol for symbol in batch_symbols}
                
                for future in as_completed(futures):
                    symbol = futures[future]
                    try:
                        result = future.result()
                        results.append(result)
                        
                        status_icon = "✅" if result["status"] == "success" else "⚠️" if result["status"] == "partial_success" else "❌"
                        timestamped_log(f"[{status_icon}] {symbol}: {result['status']}")
                    except Exception as e:
                        timestamped_log(f"[ERROR] Failed processing {symbol}: {str(e)}")
            
            # Force garbage collection between batches
            gc.collect()
        
        # Calculate average metrics for successful runs
        success_results = [r for r in results if r["status"] == "success" and r["move_metrics"]]
        
        if success_results:
            avg_accuracy = sum(r["move_metrics"].get("accuracy", 0) for r in success_results) / len(success_results)
            avg_f1 = sum(r["move_metrics"].get("f1", 0) for r in success_results) / len(success_results)
            avg_time = sum(r["duration"] for r in success_results) / len(success_results)
            
            timestamped_log(f"Training Summary:")
            timestamped_log(f"  Total symbols: {total_symbols}")
            timestamped_log(f"  Successful: {len([r for r in results if r['status'] == 'success'])}")
            timestamped_log(f"  Partial success: {len([r for r in results if r['status'] == 'partial_success'])}")
            timestamped_log(f"  Failed: {len([r for r in results if r['status'] == 'failed' or r['status'] == 'error'])}")
            timestamped_log(f"  Average metrics: Accuracy={avg_accuracy:.3f}, F1={avg_f1:.3f}")
            timestamped_log(f"  Average training time: {avg_time:.1f}s per symbol")
        else:
            timestamped_log(f"No successful training runs to calculate average metrics")

        total_time = (datetime.now() - total_start_time).total_seconds() / 60
        timestamped_log(f"Training completed in {total_time:.1f} minutes.")

    except Exception as e:
        timestamped_log(f"[ERROR] Exception during daily model training: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    train_daily_model(move_classifiers=[LIGHTGBM], direction_classifiers=[LIGHTGBM], min_days=1, max_days=5)