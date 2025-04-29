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
    """Fetch EOD candles for active symbols, calculate features, and insert into features_data table."""

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    session: Session = SessionLocal()

    try:
        # Load EOD data
        print("[INFO] Loading EOD candles...")
        eod_records = session.query(EODData).all()
        if not eod_records:
            print("[ERROR] No EOD data found.")
            return

        # Load active symbols only
        print("[INFO] Loading active Symbols...")
        symbol_records = session.query(Symbol).filter(Symbol.active == True).all()
        if not symbol_records:
            print("[ERROR] No active Symbols found.")
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
            print("[ERROR] Empty EOD or Symbol dataframe.")
            return

        # Calculate features
        print("[INFO] Calculating features...")
        features_df = calculate_features(eod_df, symbol_df)

        if features_df.empty:
            print("[ERROR] No features generated.")
            return

        # Truncate old features
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

        session.bulk_save_objects(feature_objects)
        session.commit()
        print(f"[INFO] Inserted {len(feature_objects)} features successfully.")

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Exception occurred: {e}")

    finally:
        session.close()

if __name__ == "__main__":
    create_features()
