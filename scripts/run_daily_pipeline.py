# scripts/run_daily_pipeline.py

import time
from scripts.ingest_eod_data import ingest_eod_data
from scripts.create_features import create_features
from scripts.train_all_symbols import main as train_all_symbols_main
from scripts.predict_all_symbols import main as predict_all_symbols_main

def run_daily_pipeline():
    print("\n[STEP 1] Ingesting latest EOD data...")
    ingest_eod_data()
    time.sleep(2)

    print("\n[STEP 2] Creating features...")
    create_features()
    time.sleep(2)

    print("\n[STEP 3] Training models for all symbols...")
    train_all_symbols_main()
    time.sleep(2)

    print("\n[STEP 4] Predicting for all symbols...")
    predict_all_symbols_main()
    print("\n✅ Daily pipeline completed successfully.")

if __name__ == "__main__":
    run_daily_pipeline()
