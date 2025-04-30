# scripts/run_daily_pipeline.py

import time
from scripts.ingest_eod_data import ingest_eod_data
from scripts.create_features import create_features
from scripts.parallel_train_predict import run_parallel_train_predict

def run_daily_pipeline():
    print("\n[STEP 1] Ingesting latest EOD data...")
    ingest_eod_data()
    time.sleep(2)

    print("\n[STEP 2] Creating features...")
    create_features()
    time.sleep(2)

    print("\n[STEP 3] Training + Predicting in parallel for all symbols...")
    run_parallel_train_predict()

    print("\n✅ Daily pipeline completed successfully.")

if __name__ == "__main__":
    run_daily_pipeline()
