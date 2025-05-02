# scripts/run_daily_pipeline.py

import time
import traceback
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from scripts.ingest_eod_data import ingest_eod_data
from scripts.create_features import create_features
from scripts.parallel_train_predict import run_parallel_train_predict
from db.database import check_db_connection
from core.validate.prediction_tracker import update_prediction_results
from core.validate.feedback_optimizer import batch_optimize_models

def log(msg): print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def run_step_with_recovery(step_func, step_name, max_retries=2):
    """Run a pipeline step with retry logic."""
    for attempt in range(max_retries + 1):
        try:
            log(f"[STEP] {step_name} - Starting...")
            start_time = time.time()
            
            # Run the step
            result = step_func()
            
            duration = time.time() - start_time
            log(f"[STEP] {step_name} - Completed successfully in {duration:.1f} seconds")
            return True
            
        except Exception as e:
            log(f"[ERROR] {step_name} - Attempt {attempt+1}/{max_retries+1} failed: {str(e)}")
            if attempt < max_retries:
                wait_time = 30 * (attempt + 1)  # Progressive backoff
                log(f"[RETRY] {step_name} - Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                log(f"[FATAL] {step_name} - All attempts failed. Stack trace:\n{traceback.format_exc()}")
                return False

def retrain_poor_performers():
    """Identify and retrain models that are performing poorly."""
    result = batch_optimize_models(max_symbols=5, prioritize=True)
    
    if result["status"] == "completed":
        log(f"[INFO] Model optimization completed: {result['successful']}/{result['total']} successful")
    else:
        log(f"[INFO] Model optimization status: {result['status']} - {result.get('message', '')}")
    
    return result["status"] != "error"

def run_daily_pipeline():
    """Run the complete daily pipeline with improved error handling and performance monitoring."""
    pipeline_start = datetime.now()
    log(f"[PIPELINE] Starting daily pipeline run on {pipeline_start.strftime('%Y-%m-%d')}")
    
    # Check database connection
    if not check_db_connection():
        log("[FATAL] Database connection failed. Aborting pipeline.")
        return False
    
    # Step 1: Ingest EOD data
    if not run_step_with_recovery(ingest_eod_data, "EOD Data Ingestion"):
        log("[ABORT] Pipeline stopped due to data ingestion failure")
        return False
    
    # Step 2: Update prediction verifications (validates past predictions against actual prices)
    if not run_step_with_recovery(update_prediction_results, "Prediction Validation"):
        log("[WARNING] Prediction validation failed but continuing pipeline")
    
    # Step 3: Create features
    if not run_step_with_recovery(create_features, "Feature Creation"):
        log("[ABORT] Pipeline stopped due to feature creation failure")
        return False
    
    # Step 4: Train and predict
    max_workers = 6  # Can be adjusted based on system resources
    if not run_step_with_recovery(lambda: run_parallel_train_predict(max_workers=max_workers), "Model Training & Prediction"):
        log("[WARNING] Model training and prediction had issues")
        # Continue anyway as this is not the last step
    
    # Step 5: Apply feedback loop (optimize poorly performing models)
    if not run_step_with_recovery(retrain_poor_performers, "Model Optimization"):
        log("[WARNING] Model optimization had issues")
    
    # Calculate overall duration
    pipeline_duration = (datetime.now() - pipeline_start).total_seconds()
    minutes = int(pipeline_duration // 60)
    seconds = int(pipeline_duration % 60)
    
    log(f"✅ Daily pipeline completed in {minutes} minutes and {seconds} seconds")
    
    # Return success status
    return True

if __name__ == "__main__":
    success = run_daily_pipeline()
    exit(0 if success else 1)  # Exit with status code for cron jobs