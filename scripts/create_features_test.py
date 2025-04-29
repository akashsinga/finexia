# scripts/create_features_test.py

import pandas as pd
from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from db.models.eod_data import EODData
from db.models.symbol import Symbol
from db.models.feature_data import FeatureData
from db.base_class import Base
from core.features.feature_engineer import calculate_features
from sqlalchemy import text

def create_features_for_one_symbol(target_symbol: str = "RELIANCE"):
    """Fetch EOD candles, calculate features, and insert into features_data table for one symbol (testing only)."""

    # Ensure table exists
    Base.metadata.create_all(bind=engine)

    session: Session = SessionLocal()

    # Load target symbol
    print(f"[INFO] Loading symbol {target_symbol}...")
    symbol = session.query(Symbol).filter(Symbol.trading_symbol == target_symbol, Symbol.active == True).first()

    if not symbol:
        print(f"[ERROR] Symbol {target_symbol} not found!")
        session.close()
        return

    # Load EOD data for the symbol
    print(f"[INFO] Loading EOD candles for {target_symbol}...")
    eod_records = session.query(EODData).filter(EODData.trading_symbol == target_symbol).all()

    if not eod_records:
        print(f"[ERROR] No EOD data found for {target_symbol}!")
        session.close()
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
        "trading_symbol": symbol.trading_symbol,
        "fo_eligible": symbol.fo_eligible
    }])

    if eod_df.empty:
        print("[ERROR] Empty EOD dataframe after loading.")
        session.close()
        return

    # Calculate features
    print("[INFO] Calculating features...")
    features_df = calculate_features(eod_df, symbol_df)

    if features_df.empty:
        print("[ERROR] No features generated.")
        session.close()
        return

    # Truncate feature_data table first
    print("[INFO] Truncating old features...")
    session.execute(text(f"TRUNCATE TABLE {FeatureData.__tablename__} RESTART IDENTITY;"))
    session.commit()

    # Insert new features
    print(f"[INFO] Inserting {len(features_df)} feature records...")
    feature_objects = []
    for _, row in features_df.iterrows():
        feature = FeatureData(
            trading_symbol=row["trading_symbol"],
            exchange=row["exchange"],
            date=row["date"],
            week_day = row["week_day"],
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
            fo_eligible=row['fo_eligible'],
            rsi_14=row["rsi_14"],
            close_ema50_gap_pct=row["close_ema50_gap_pct"],
            open_gap_pct=row["open_gap_pct"],
            macd_histogram=row["macd_histogram"],
            atr_14_normalized=row["atr_14_normalized"]
        )
        feature_objects.append(feature)

    try:
        session.bulk_save_objects(feature_objects)
        session.commit()
        print(f"[INFO] Inserted {len(feature_objects)} features successfully.")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Failed to insert features: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_features_for_one_symbol(target_symbol="ADANIENT")  # <-- You can change this easily
