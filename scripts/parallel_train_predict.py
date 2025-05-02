# scripts/parallel_train_predict.py

from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import time
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.database import SessionLocal
from db.models.symbol import Symbol
from core.train.daily_trainer import train_models_for_one_symbol
from core.predict.daily_predictor import predict_for_one_symbol
from core.config import LIGHTGBM, DEFAULT_DAILY_STRONG_MOVE_THRESHOLD

def log(msg): print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def train_and_predict(symbol: str) -> str:
    """Train and predict for a single symbol with improved error handling and metrics."""
    start_time = time.time()
    
    try:
        # Train models
        log(f"[TRAIN] Starting for {symbol}...")
        train_start = time.time()
        
        # Use LIGHTGBM instead of RANDOM_FOREST for much faster training
        # Reduce max_days from 10 to 5 for faster processing
        train_models_for_one_symbol(symbol=symbol, move_classifiers=[LIGHTGBM], direction_classifiers=[LIGHTGBM], threshold_percent=DEFAULT_DAILY_STRONG_MOVE_THRESHOLD, min_days=1, max_days=5)
        
        train_duration = time.time() - train_start
        
        # Run prediction
        log(f"[PREDICT] Starting for {symbol}...")
        predict_start = time.time()
        predict_success = predict_for_one_symbol(symbol=symbol)
        predict_duration = time.time() - predict_start
        
        total_duration = time.time() - start_time
        
        result_status = "✅" if predict_success else "⚠️"
        return f"[{result_status}] {symbol}: Trained in {train_duration:.1f}s + Predicted in {predict_duration:.1f}s = {total_duration:.1f}s total"

    except Exception as e:
        duration = time.time() - start_time
        return f"[❌] {symbol}: Failed after {duration:.1f}s - {str(e)}"

def run_parallel_train_predict(max_workers: int = 8):
    """Run parallel training and prediction with improved monitoring and error handling."""
    session: Session = SessionLocal()
    start_time = datetime.now()
    
    try:
        # Get symbols
        symbols = session.query(Symbol.trading_symbol).filter(Symbol.active == True).all()
        symbol_list = [s.trading_symbol for s in symbols]
        total_symbols = len(symbol_list)
        
        if not total_symbols:
            log("[ERROR] No active symbols found.")
            return
            
        log(f"[INFO] Running parallel training + prediction for {total_symbols} symbols with {max_workers} workers...")
        
        # Optimize worker count based on available CPU cores
        cpu_count = os.cpu_count() or 4
        adjusted_workers = min(max_workers, cpu_count - 1, total_symbols)
        if adjusted_workers != max_workers:
            log(f"[INFO] Adjusted worker count to {adjusted_workers} based on available resources")
            max_workers = adjusted_workers
        
        # Process in parallel
        successful, failed = 0, 0
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(train_and_predict, symbol): symbol for symbol in symbol_list}
            
            for i, future in enumerate(as_completed(futures)):
                symbol = futures[future]
                try:
                    result = future.result()
                    log(result)
                    
                    if result.startswith("[✅]"):
                        successful += 1
                    elif result.startswith("[❌]"):
                        failed += 1
                        
                    # Progress update
                    if (i + 1) % 5 == 0 or (i + 1) == total_symbols:
                        elapsed = (datetime.now() - start_time).total_seconds() / 60
                        remaining = elapsed / (i + 1) * (total_symbols - i - 1)
                        completion_pct = (i + 1) / total_symbols * 100
                        log(f"[PROGRESS] {i+1}/{total_symbols} ({completion_pct:.1f}%) symbols processed. "
                            f"Success: {successful}, Failed: {failed}. "
                            f"Elapsed: {elapsed:.1f}m, Remaining: {remaining:.1f}m")
                        
                except Exception as e:
                    log(f"[❌] {symbol}: Unexpected error: {str(e)}")
                    failed += 1
        
        # Final stats
        duration = (datetime.now() - start_time).total_seconds() / 60
        avg_time_per_symbol = duration * 60 / total_symbols if total_symbols else 0
        
        log(f"[COMPLETE] Training and prediction completed in {duration:.1f} minutes.")
        log(f"[STATS] Total: {total_symbols}, Successful: {successful}, Failed: {failed}, "
            f"Success rate: {successful/total_symbols*100:.1f}%, "
            f"Avg time per symbol: {avg_time_per_symbol:.1f}s")

    except SQLAlchemyError as e:
        log(f"[ERROR] Database error: {str(e)}")