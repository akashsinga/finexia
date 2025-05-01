# scripts/fetch_eod_data.py

import time
import random
import threading
import requests
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from sqlalchemy.exc import SQLAlchemyError
from db.models.symbol import Symbol
from db.models.eod_data import EODData
from db.base_class import Base
from scripts.constants import (DHAN_CHARTS_HISTORICAL_URL, INDIA_TZ, HEADERS, 
                             SAFE_SLEEP_BETWEEN_REQUESTS, MAX_RETRIES, RETRY_BACKOFF_FACTOR, 
                             RETRY_INITIAL_WAIT)
from db.database import DATABASE_URL

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Rate limiting lock
rate_limit_lock = threading.Semaphore(1)  # Only 1 API request at a time

def log(msg): print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

class CircuitBreaker:
    """Circuit breaker to prevent excessive API calls during failures."""
    def __init__(self, fail_threshold=5, reset_timeout=60):
        self.fail_count = 0
        self.fail_threshold = fail_threshold
        self.reset_timeout = reset_timeout
        self.last_failure_time = None
        self.is_open = False
        self.lock = threading.Lock()
        
    def allow_request(self):
        with self.lock:
            if not self.is_open:
                return True
            
            if self.last_failure_time and time.time() - self.last_failure_time > self.reset_timeout:
                self.is_open = False
                self.fail_count = 0
                return True
                
            return False
            
    def record_failure(self):
        with self.lock:
            self.fail_count += 1
            self.last_failure_time = time.time()
            if self.fail_count >= self.fail_threshold:
                self.is_open = True
                log(f"[ALERT] Circuit breaker triggered - pausing requests for {self.reset_timeout}s")

# Global circuit breaker
circuit_breaker = CircuitBreaker()

def fetch_eod_from_dhan(symbol: str, security_id: str, instrument_type: str, exchange_segment: str, from_date: str, to_date: str) -> dict:
    """Fetch EOD data from Dhan API with improved error handling and circuit breaker."""
    if not circuit_breaker.allow_request():
        log(f"[CIRCUIT] Skipping {symbol} - circuit breaker active")
        return None
        
    payload = {
        "securityId": str(security_id),
        "exchangeSegment": exchange_segment,
        "instrument": instrument_type,
        "expiryCode": 0,
        "oi": False,
        "fromDate": from_date,
        "toDate": to_date
    }

    for attempt in range(MAX_RETRIES):
        try:
            # Apply rate limiting
            with rate_limit_lock:
                response = requests.post(DHAN_CHARTS_HISTORICAL_URL, headers=HEADERS, json=payload, timeout=30)
                # Add jitter to sleep time to prevent synchronized retries
                time.sleep(SAFE_SLEEP_BETWEEN_REQUESTS + random.uniform(0.1, 0.5))
                
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if hasattr(e, 'response') and e.response else "UNKNOWN"
            
            if status == 429:  # Rate limit
                circuit_breaker.record_failure()
                wait = RETRY_INITIAL_WAIT * (RETRY_BACKOFF_FACTOR ** attempt) + random.uniform(0.1, 0.5)
                log(f"[RETRY] {symbol} hit 429 rate limit. Waiting {wait:.1f}s... (Attempt {attempt+1}/{MAX_RETRIES})")
                time.sleep(wait)
            elif status == 403:  # Auth error
                log(f"[AUTH ERROR] {symbol} hit 403. Check credentials.")
                break
            elif status == 400:  # Bad request
                log(f"[BAD REQUEST] {symbol} hit 400. Likely invalid securityId/segment.")
                break
            else:
                log(f"[HTTP ERROR] {symbol}: {status} - {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_INITIAL_WAIT * (RETRY_BACKOFF_FACTOR ** attempt)
                    time.sleep(wait)
                else:
                    break
                    
        except requests.exceptions.ConnectionError as e:
            circuit_breaker.record_failure()
            log(f"[CONNECTION ERROR] {symbol}: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                wait = RETRY_INITIAL_WAIT * (RETRY_BACKOFF_FACTOR ** attempt) * 2  # Longer wait for connection issues
                time.sleep(wait)
            else:
                break
                
        except requests.exceptions.Timeout as e:
            log(f"[TIMEOUT] {symbol}: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                wait = RETRY_INITIAL_WAIT * (RETRY_BACKOFF_FACTOR ** attempt)
                time.sleep(wait)
            else:
                break
                
        except Exception as e:
            log(f"[ERROR] Fetch failed for {symbol}: {str(e)}")
            break

    return None

def create_eod_objects(symbol_dict, data, after_date: datetime.date):
    """Create EOD objects from API response with data validation."""
    if not data or "timestamp" not in data:
        return [], 0, 0
        
    seen_dates = set()
    candles = []
    skipped_old = 0
    skipped_dupe = 0

    try:
        ts_list = data.get("timestamp", [])
        open_list = data.get("open", [])
        high_list = data.get("high", [])
        low_list = data.get("low", [])
        close_list = data.get("close", [])
        volume_list = data.get("volume", [])
        
        # Validate lengths match
        if not (len(ts_list) == len(open_list) == len(high_list) == 
                len(low_list) == len(close_list) == len(volume_list)):
            log(f"[WARNING] Data length mismatch for {symbol_dict['trading_symbol']}")
            return [], 0, 0
            
        for i, ts in enumerate(ts_list):
            # Convert timestamp to date
            dt = datetime.fromtimestamp(ts, tz=INDIA_TZ).date()
            
            # Skip old data
            if dt <= after_date:
                skipped_old += 1
                continue
                
            # Skip duplicates
            if dt in seen_dates:
                skipped_dupe += 1
                continue

            seen_dates.add(dt)
            
            # Data validation
            try:
                open_val = float(open_list[i])
                high_val = float(high_list[i])
                low_val = float(low_list[i])
                close_val = float(close_list[i])
                volume_val = int(volume_list[i])
                
                # Skip invalid data
                if (open_val <= 0 or high_val <= 0 or low_val <= 0 or close_val <= 0 or
                    high_val < low_val or high_val < open_val or high_val < close_val or
                    low_val > open_val or low_val > close_val):
                    log(f"[WARNING] Invalid price data for {symbol_dict['trading_symbol']} on {dt}")
                    continue
                    
                # Create EOD object
                candles.append(EODData(
                    trading_symbol=symbol_dict["trading_symbol"],
                    exchange=symbol_dict["exchange"],
                    date=dt,
                    open=open_val,
                    high=high_val,
                    low=low_val,
                    close=close_val,
                    volume=volume_val,
                    fo_eligible=symbol_dict["fo_eligible"]
                ))
            except (ValueError, TypeError) as e:
                log(f"[WARNING] Invalid data format for {symbol_dict['trading_symbol']} on {dt}: {e}")
                
    except Exception as e:
        log(f"[WARNING] Failed parsing {symbol_dict['trading_symbol']}: {str(e)}")
        
    return candles, skipped_old, skipped_dupe

def fetch_and_insert_one_symbol(symbol_dict, from_date, to_date, last_date_lookup):
    """Fetch and insert EOD data for one symbol with optimized database operations."""
    session = SessionLocal()
    start_time = time.time()
    
    try:
        symbol = symbol_dict["trading_symbol"]
        # Determine start date - use last EOD date + 1 day if available
        after_date = last_date_lookup.get(symbol)
        
        if after_date:
            fetch_from_date = (after_date + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            fetch_from_date = from_date
            after_date = datetime.strptime(from_date, "%Y-%m-%d").date() - timedelta(days=1)

        # Fetch data
        data = fetch_eod_from_dhan(
            symbol=symbol,
            security_id=symbol_dict["security_id"],
            instrument_type=symbol_dict["instrument_type"],
            exchange_segment=symbol_dict["segment"],
            from_date=fetch_from_date,
            to_date=to_date
        )

        if data is None:
            return f"[FAIL] {symbol} - fetch failed"
            
        if "timestamp" not in data or not data["timestamp"]:
            return f"[SKIP] {symbol} - no candle data"

        # Process data
        candles, skip_old, skip_dup = create_eod_objects(symbol_dict, data, after_date)
        
        if not candles:
            return f"[SKIP] {symbol} - all old ({skip_old}) or dupes ({skip_dup})"

        # Bulk insert
        session.bulk_save_objects(candles)
        session.commit()
        
        elapsed = time.time() - start_time
        return f"[OK] {symbol} - inserted {len(candles)} in {elapsed:.2f}s, skipped: {skip_old} old, {skip_dup} dupes"

    except SQLAlchemyError as e:
        session.rollback()
        return f"[DB ERROR] {symbol_dict['trading_symbol']}: {str(e)}"
    except Exception as e:
        session.rollback()
        return f"[ERROR] {symbol_dict['trading_symbol']} failed: {str(e)}"
    finally:
        session.close()

def fetch_eod_data(from_date: str, to_date: str, max_workers: int = 5):
    """Fetch EOD data for all active symbols with improved concurrency and monitoring."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    start_time = datetime.now()
    
    try:
        # Get all active symbols
        symbols = session.query(Symbol).filter(Symbol.active == True).all()
        
        if not symbols:
            log("[WARNING] No active symbols found.")
            return
            
        symbol_dicts = [{
            "security_id": str(s.security_id),
            "trading_symbol": s.trading_symbol,
            "exchange": s.exchange,
            "instrument_type": s.instrument_type,
            "segment": s.segment,
            "fo_eligible": s.fo_eligible
        } for s in symbols]

        # Get latest EOD date for each symbol
        last_dates = session.query(EODData.trading_symbol, func.max(EODData.date)).group_by(EODData.trading_symbol).all()
        
        last_date_lookup = {symbol: date for symbol, date in last_dates}
        
        log(f"[INFO] EOD fetch from {from_date} to {to_date} for {len(symbol_dicts)} symbols with {max_workers} threads.")

        # Process symbols in parallel
        completed, failed = 0, 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_and_insert_one_symbol, sym_dict, from_date, to_date, last_date_lookup): sym_dict["trading_symbol"] for sym_dict in symbol_dicts}
            
            for i, future in enumerate(as_completed(futures)):
                symbol = futures[future]
                result = future.result()
                log(result)
                
                if result.startswith("[OK]"):
                    completed += 1
                elif result.startswith("[FAIL]") or result.startswith("[ERROR]") or result.startswith("[DB ERROR]"):
                    failed += 1
                
                # Progress update
                if (i + 1) % 10 == 0 or (i + 1) == len(symbol_dicts):
                    elapsed = (datetime.now() - start_time).total_seconds() / 60
                    remain = elapsed / (i + 1) * (len(symbol_dicts) - i - 1)
                    log(f"[PROGRESS] {i+1}/{len(symbol_dicts)}, Success: {completed}, "
                        f"Failed: {failed}, Elapsed: {elapsed:.1f}m, Remaining: {remain:.1f}m")

        duration = (datetime.now() - start_time).total_seconds() / 60
        log(f"✅ EOD data fetch completed in {duration:.1f} minutes. Success: {completed}/{len(symbol_dicts)}")

    except Exception as e:
        session.rollback()
        log(f"[ERROR] fetch_eod_data failed: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    from scripts.constants import FROM_DATE, TO_DATE
    fetch_eod_data(from_date=FROM_DATE, to_date=TO_DATE)
