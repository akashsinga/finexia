# scripts/create_features.py

import time
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db.base_class import Base
from db.database import DATABASE_URL
from db.models.eod_data import EODData
from db.models.symbol import Symbol
from db.models.feature_data import FeatureData
from core.features.feature_engineer import calculate_features

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def log(msg): print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def generate_and_insert_features(symbol: str, eod_df: pd.DataFrame, symbol_meta_df: pd.DataFrame, feature_pairs: set):
    session = SessionLocal()
    try:
        symbol_eod = eod_df[eod_df["trading_symbol"] == symbol]
        missing_dates = [d for d in symbol_eod["date"].unique() if (symbol, d) not in feature_pairs]
        symbol_eod = symbol_eod[symbol_eod["date"].isin(missing_dates)]

        if symbol_eod.empty:
            return f"[SKIP] {symbol} - no missing dates"

        symbol_meta = symbol_meta_df[symbol_meta_df["trading_symbol"] == symbol]
        if symbol_meta.empty:
            return f"[ERROR] {symbol} - symbol metadata missing"

        features_df = calculate_features(symbol_eod, symbol_meta)

        if features_df.empty:
            return f"[SKIP] {symbol} - no features generated"

        feature_objects = [
            FeatureData(
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
                atr_14_normalized=row["atr_14_normalized"],
                percent_move=row["percent_move"] 
            )
            for _, row in features_df.iterrows()
        ]

        session.bulk_save_objects(feature_objects)
        session.commit()
        return f"[OK] {symbol} - inserted {len(feature_objects)} features"

    except Exception as e:
        session.rollback()
        return f"[FAIL] {symbol} - {e}"
    finally:
        session.close()

def create_features(max_workers: int = 6):
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        log("[INFO] Loading EOD and Symbol data...")
        eod_records = session.query(EODData).all()
        symbol_records = session.query(Symbol).filter(Symbol.active == True).all()
        existing_features = session.query(FeatureData.trading_symbol, FeatureData.date).all()

        if not eod_records or not symbol_records:
            log("[ERROR] Missing EOD or Symbol data. Exiting.")
            return

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

        feature_pairs = set((r.trading_symbol, r.date) for r in existing_features)
        all_symbols = eod_df["trading_symbol"].unique()

        log(f"[INFO] Starting parallel feature generation for {len(all_symbols)} symbols...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(generate_and_insert_features, sym, eod_df, symbol_df, feature_pairs)
                for sym in all_symbols
            ]
            for f in as_completed(futures):
                log(f.result())

        log("[SUCCESS] Feature generation completed.")
    except Exception as e:
        log(f"[ERROR] Failed during create_features: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_features()
