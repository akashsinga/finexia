# scripts/create_features.py

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.database import SessionLocal, engine
from db.models.eod_data import EODData
from db.models.symbol import Symbol
from db.models.feature_data import FeatureData
from db.base_class import Base
from core.features.feature_engineer import calculate_features

def create_features():
    """Fetch EOD candles, calculate features, and insert into features_data table."""

    # Ensure table is created
    Base.metadata.create_all(bind=engine)

    session: Session = SessionLocal()

    # Load EOD data
    print("[INFO] Loading EOD candles...")
    eod_records = session.query(EODData).all()
    if not eod_records:
        print("[ERROR] No EOD data found.")
        return

    # Load Symbol master
    print("[INFO] Loading Symbol master...")
    symbol_records = session.query(Symbol).all()
    if not symbol_records:
        print("[ERROR] No Symbols found.")
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

    if eod_df.empty:
        print("[ERROR] Empty EOD dataframe.")
        return

    # Calculate features
    print("[INFO] Calculating features...")
    features_df = calculate_features(eod_df, symbol_df)

    if features_df.empty:
        print("[ERROR] No features generated.")
        return

    # Check for schema mismatch (optional advanced step, for future upgrades)
    # For now, we proceed with complete deletion every run.

    # Truncate features_data table before inserting
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
            price_change_t_1=row["price_change_t_1"],
            gap_pct=row["gap_pct"],
            hl_range=row["hl_range"],
            body_to_range_ratio=row["body_to_range_ratio"],
            lower_wick_pct=row["lower_wick_pct"],
            upper_wick_pct=row["upper_wick_pct"],
            closing_strength=row["closing_strength"],
            distance_from_ema_5=row["distance_from_ema_5"],
            return_3d=row["return_3d"],
            return_5d=row["return_5d"],
            position_in_range_5d=row["position_in_range_5d"],
            atr_5=row["atr_5"],
            volume_spike_ratio=row["volume_spike_ratio"],
            range_compression_ratio=row["range_compression_ratio"],
            volatility_squeeze=row["volatility_squeeze"],
            trend_zone_strength=row["trend_zone_strength"],
            fo_eligible=row["fo_eligible"]
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
    create_features()
