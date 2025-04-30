# scripts/create_features.py

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from db.database import SessionLocal, engine
from db.models.eod_data import EODData
from db.models.symbol import Symbol
from db.models.feature_data import FeatureData
from db.base_class import Base
from core.features.feature_engineer import calculate_features

def split_list(lst, batch_size):
    """Split a list into smaller batches."""
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]

def create_features():
    """Incrementally create features for (symbol, date) pairs missing in features_data."""

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    session: Session = SessionLocal()

    try:
        # Load EOD data
        print("[INFO] Loading EOD candles...")
        eod_records = session.query(EODData).all()
        if not eod_records:
            print("[ERROR] No EOD data found. Exiting.")
            return

        # Load active symbols
        print("[INFO] Loading active Symbols...")
        symbol_records = session.query(Symbol).filter(Symbol.active == True).all()
        if not symbol_records:
            print("[ERROR] No active Symbols found. Exiting.")
            return

        # Convert to DataFrames
        eod_df = pd.DataFrame([{
            "trading_symbol": r.trading_symbol,
            "exchange": r.exchange,
            "date": r.date,
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume
        } for r in eod_records])

        symbol_df = pd.DataFrame([{
            "trading_symbol": s.trading_symbol,
            "fo_eligible": s.fo_eligible
        } for s in symbol_records])

        if eod_df.empty or symbol_df.empty:
            print("[ERROR] Empty EOD or Symbol dataframe. Exiting.")
            return

        # Load existing features
        print("[INFO] Checking existing features...")
        feature_pairs = set(
            (row.trading_symbol, row.date) for row in session.query(FeatureData.trading_symbol, FeatureData.date)
        )
        eod_pairs = set(
            (row.trading_symbol, row.date) for row in eod_records
        )

        missing_pairs = eod_pairs - feature_pairs

        if not missing_pairs:
            print("[INFO] No missing (symbol, date) pairs found. Features already up-to-date.")
            return

        print(f"[INFO] Found {len(missing_pairs)} missing (symbol, date) records.")

        # Filter EOD data for missing records
        eod_df["pair"] = list(zip(eod_df["trading_symbol"], eod_df["date"]))
        eod_df = eod_df[eod_df["pair"].isin(missing_pairs)].drop(columns=["pair"])

        # Calculate features
        print("[INFO] Calculating features for missing records...")
        features_df = calculate_features(eod_df, symbol_df)

        if features_df.empty:
            print("[ERROR] No features generated after filtering. Exiting.")
            return

        print(f"[INFO] Calculated {len(features_df)} feature rows ready for insertion.")

        # Prepare feature objects
        feature_objects = []
        for _, row in features_df.iterrows():
            feature = FeatureData(
                trading_symbol=row["trading_symbol"],
                exchange=row["exchange"],
                date=row["date"],
                week_day=row["week_day"],
                volatility_squeeze=row["volatility_squeeze"],
                trend_zone_strength=row["trend_zone_strength"],
                range_compression_ratio=row["range_compression_ratio"],
                volume_spike_ratio=row["volume_spike_ratio"],
                body_to_range_ratio=row["body_to_range_ratio"],
                distance_from_ema_5=row["distance_from_ema_5"],
                gap_pct=row["gap_pct"],
                return_3d=row["return_3d"],
                atr_5=row["atr_5"],
                hl_range=row["hl_range"],
                fo_eligible=row["fo_eligible"],
                rsi_14=row["rsi_14"],
                close_ema50_gap_pct=row["close_ema50_gap_pct"],
                open_gap_pct=row["open_gap_pct"],
                macd_histogram=row["macd_histogram"],
                atr_14_normalized=row["atr_14_normalized"]
            )
            feature_objects.append(feature)

        # Insert in batches
        batch_size = 10000
        total_inserted = 0

        print(f"[INFO] Inserting features into database in batches of {batch_size}...")
        for idx, batch in enumerate(split_list(feature_objects, batch_size)):
            try:
                session.bulk_save_objects(batch, return_defaults=False)
                session.commit()
                total_inserted += len(batch)
                print(f"[INFO] Batch {idx+1}: Inserted {len(batch)} features successfully.")
            except Exception as e:
                session.rollback()
                print(f"[ERROR] Batch {idx+1}: Failed to insert features: {e}")

        print(f"[SUCCESS] Inserted total {total_inserted} new features into features_data.")

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Exception occurred: {e}")

    finally:
        session.close()

if __name__ == "__main__":
    create_features()
