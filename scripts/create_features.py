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

def process_symbol(symbol: str):
    session = SessionLocal()
    try:
        sym_obj = session.query(Symbol).filter(Symbol.trading_symbol == symbol, Symbol.active == True).first()
        if not sym_obj:
            return f"[SKIP] {symbol} - symbol not active"

        eod_rows = session.query(EODData).filter(EODData.trading_symbol == symbol).all()
        if not eod_rows:
            return f"[SKIP] {symbol} - no EOD data"

        feature_dates = session.query(FeatureData.date).filter(FeatureData.trading_symbol == symbol).all()
        existing_dates = set([row.date for row in feature_dates])

        eod_data = [{
            "trading_symbol": r.trading_symbol,
            "exchange": r.exchange,
            "date": r.date,
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume
        } for r in eod_rows if r.date not in existing_dates]

        if not eod_data:
            return f"[SKIP] {symbol} - all features already present"

        eod_df = pd.DataFrame(eod_data)
        symbol_df = pd.DataFrame([{
            "trading_symbol": sym_obj.trading_symbol,
            "fo_eligible": sym_obj.fo_eligible
        }])

        features_df = calculate_features(eod_df, symbol_df)

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
        symbols = session.query(Symbol.trading_symbol).filter(Symbol.active == True).all()
        if not symbols:
            log("[ERROR] No active symbols found.")
            return

        symbol_list = [s.trading_symbol for s in symbols]

        log(f"[INFO] Starting parallel feature generation for {len(symbol_list)} symbols...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_symbol, sym) for sym in symbol_list]
            for f in as_completed(futures):
                log(f.result())

        log("[SUCCESS] Feature generation completed.")

    except Exception as e:
        log(f"[ERROR] Failed during create_features: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_features()
