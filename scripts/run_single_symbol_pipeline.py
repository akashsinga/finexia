# scripts/run_single_symbol_pipeline.py

import time
from scripts.ingest_eod_data import ingest_eod_data
from scripts.create_features_test import create_features_for_one_symbol
from scripts.train_single_symbol import main as train_single_symbol_main
from scripts.predict_single_symbol import main as predict_single_symbol_main

def run_single_symbol_pipeline():
    target_symbol = "INDHOTEL"  # <-- Change here if you want to test for different symbol

    print("\n[STEP 1] Ingesting latest EOD data...")
    # ingest_eod_data()
    time.sleep(2)

    print(f"\n[STEP 2] Creating features for {target_symbol}...")
    create_features_for_one_symbol(target_symbol=target_symbol)
    time.sleep(2)

    print(f"\n[STEP 3] Training models for {target_symbol}...")
    train_single_symbol_main(symbol=target_symbol)
    time.sleep(2)

    print(f"\n[STEP 4] Predicting for {target_symbol}...")
    predict_single_symbol_main(symbol=target_symbol)

    print("\n✅ Single Symbol Daily Pipeline completed successfully.")

if __name__ == "__main__":
    run_single_symbol_pipeline()
