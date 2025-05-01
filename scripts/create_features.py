# scripts/create_features.py

import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import create_engine, func
from db.base_class import Base
from db.database import DATABASE_URL, SessionLocal
from db.models.eod_data import EODData
from db.models.symbol import Symbol
from db.models.feature_data import FeatureData
from core.features.feature_engineer import calculate_features

# Create engine
engine = create_engine(DATABASE_URL)

def log(msg): print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def get_latest_feature_dates(session, symbol):
    """Get the latest feature date for a symbol more efficiently."""
    result = session.query(func.max(FeatureData.date)).filter(FeatureData.trading_symbol == symbol).first()
    return result[0] if result and result[0] else None

def process_symbol(symbol: str):
    """Process a single symbol with optimized database operations."""
    session = SessionLocal()
    
    try:
        # Check if symbol is active
        sym_obj = session.query(Symbol).filter(Symbol.trading_symbol == symbol, Symbol.active == True).first()
        if not sym_obj:
            return f"[SKIP] {symbol} - symbol not active"

        # Get EOD data
        eod_query = session.query(EODData).filter(EODData.trading_symbol == symbol)
        eod_count = eod_query.count()
        
        if eod_count == 0:
            return f"[SKIP] {symbol} - no EOD data"

        # Get latest feature date
        latest_feature_date = get_latest_feature_dates(session, symbol)
        
        # Build query for EOD data that needs features
        if latest_feature_date:
            eod_query = eod_query.filter(EODData.date > latest_feature_date)
        
        eod_rows = eod_query.all()
        if not eod_rows:
            return f"[SKIP] {symbol} - all features already present"

        # Convert to dictionary for efficient DataFrame creation
        eod_data = [{
            "trading_symbol": r.trading_symbol,
            "exchange": r.exchange,
            "date": r.date,
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume
        } for r in eod_rows]

        # Need historical data for proper feature calculation (lookback periods)
        if latest_feature_date:
            # Add some additional lookback data to ensure proper feature calculation
            lookback_days = 50  # Enough for longer-period indicators
            lookback_data = session.query(EODData).filter(
                EODData.trading_symbol == symbol,
                EODData.date <= latest_feature_date
            ).order_by(EODData.date.desc()).limit(lookback_days).all()
            
            eod_data.extend([{
                "trading_symbol": r.trading_symbol,
                "exchange": r.exchange,
                "date": r.date,
                "open": r.open,
                "high": r.high,
                "low": r.low,
                "close": r.close,
                "volume": r.volume
            } for r in lookback_data])

        # Convert to DataFrames        
        eod_df = pd.DataFrame(eod_data)
        symbol_df = pd.DataFrame([{
            "trading_symbol": sym_obj.trading_symbol,
            "fo_eligible": sym_obj.fo_eligible
        }])

        # Calculate features
        features_df = calculate_features(eod_df, symbol_df)
        
        if features_df.empty:
            return f"[SKIP] {symbol} - no features generated"

        # Filter out features we already have
        if latest_feature_date:
            features_df = features_df[features_df["date"] > latest_feature_date]

        if features_df.empty:
            return f"[SKIP] {symbol} - no new features to add"

        # Create feature objects
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

        # Bulk insert for better performance
        session.bulk_save_objects(feature_objects)
        session.commit()
        return f"[OK] {symbol} - inserted {len(feature_objects)} features"

    except Exception as e:
        session.rollback()
        return f"[FAIL] {symbol} - {str(e)}"
    finally:
        session.close()

def create_features(max_workers: int = 6):
    """Create features for all active symbols with improved concurrency and error handling."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    start_time = datetime.now()
    
    try:
        # Get all active symbols
        symbols = session.query(Symbol.trading_symbol).filter(Symbol.active == True).all()
        if not symbols:
            log("[ERROR] No active symbols found.")
            return

        symbol_list = [s.trading_symbol for s in symbols]
        total_symbols = len(symbol_list)
        
        log(f"[INFO] Starting parallel feature generation for {total_symbols} symbols...")

        # Process symbols in parallel with optimized thread pool
        successful, failed = 0, 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_symbol, sym): sym for sym in symbol_list}
            
            for i, future in enumerate(as_completed(futures)):
                symbol = futures[future]
                result = future.result()
                log(result)
                
                if result.startswith("[OK]"):
                    successful += 1
                elif result.startswith("[FAIL]"):
                    failed += 1
                
                # Progress update
                if (i + 1) % 10 == 0 or (i + 1) == total_symbols:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    remain = (elapsed / (i + 1)) * (total_symbols - i - 1)
                    log(f"[PROGRESS] {i+1}/{total_symbols} symbols, "
                        f"Success: {successful}, Failed: {failed}, "
                        f"Elapsed: {elapsed:.1f}s, Remaining: {remain:.1f}s")

        duration = (datetime.now() - start_time).total_seconds()
        log(f"[SUCCESS] Feature generation completed in {duration:.1f} seconds. "
            f"Successful: {successful}/{total_symbols}")

    except Exception as e:
        log(f"[ERROR] Failed during create_features: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    create_features()