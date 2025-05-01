# scripts/run_daily_pipeline.py

import time
from datetime import datetime
from scripts.ingest_eod_data import ingest_eod_data
from scripts.create_features import create_features
from scripts.parallel_train_predict import run_parallel_train_predict

def log(msg): print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def run_daily_pipeline():
    log("[STEP 1] Ingesting EOD data (historical + today's)...")
    ingest_eod_data()
    time.sleep(1)

    log("[STEP 2] Creating missing features...")
    create_features()
    time.sleep(1)

    log("[STEP 3] Training + predicting in parallel...")
    run_parallel_train_predict(max_workers=6)

    log("✅ Daily pipeline completed successfully.")

if __name__ == "__main__":
    run_daily_pipeline()
