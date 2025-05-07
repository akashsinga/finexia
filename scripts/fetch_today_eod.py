# scripts/fetch_today_eod.py

import time
import random
import threading
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.database import SessionLocal, engine
from db.models.symbol import Symbol
from db.models.eod_data import EODData
from db.base_class import Base
from scripts.constants import DHAN_TODAY_EOD_URL, HEADERS, INDIA_TZ, SAFE_SLEEP_BETWEEN_REQUESTS, MAX_RETRIES

# Rate limiting lock
rate_limit_lock = threading.Semaphore(1)


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def split_list(lst, size):
    """Split a list into chunks of specified size."""
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def retry_with_backoff(func, max_retries=MAX_RETRIES):
    """Retry a function with exponential backoff."""

    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = (2**attempt) + random.uniform(0.1, 0.5)
                log(f"Request failed: {e}. Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)

    return wrapper


@retry_with_backoff
def fetch_batch(segment: str, chunk: list[int], batch_idx: int, total_batches: int, today_date: datetime.date, id_to_symbol: dict) -> str:
    """Fetch and process a batch of symbols."""
    session = SessionLocal()
    start_time = time.time()

    try:
        # Prepare payload
        payload = {segment: chunk}

        # Make API request with rate limiting
        with rate_limit_lock:
            response = requests.post(DHAN_TODAY_EOD_URL, headers=HEADERS, json=payload, timeout=30)
            time.sleep(SAFE_SLEEP_BETWEEN_REQUESTS + random.uniform(0.1, 0.5))

        # Validate response
        response.raise_for_status()
        result = response.json()

        # Check for API error responses
        if result.get("status") != "success":
            error_msg = result.get("message", "Unknown API error")
            log(f"[API ERROR] {segment} batch {batch_idx}: {error_msg}")
            return f"[FAIL] {segment} batch {batch_idx}/{total_batches} - API error: {error_msg}"

        # Extract data
        data = result.get("data", {}).get(segment, {})
        if not data:
            return f"[EMPTY] {segment} batch {batch_idx}/{total_batches} - No data returned"

        # Process quotes data
        processed = 0
        success_count = 0

        for sec_id_str, quote in data.items():
            try:
                sid = int(sec_id_str)
                sym = id_to_symbol.get(sid)
                if not sym:
                    continue

                processed += 1
                ohlc = quote.get("ohlc", {})

                if not all(k in ohlc for k in ["open", "high", "low", "close"]):
                    continue

                # Try to find existing record
                existing = session.query(EODData).filter(EODData.trading_symbol == sym.trading_symbol, EODData.date == today_date).first()

                if existing:
                    # Update existing record
                    existing.open = float(ohlc.get("open", 0))
                    existing.high = float(ohlc.get("high", 0))
                    existing.low = float(ohlc.get("low", 0))
                    existing.close = float(ohlc.get("close", 0))
                    existing.volume = int(quote.get("volume", 0))
                    existing.fo_eligible = sym.fo_eligible
                    existing.exchange = sym.exchange  # Ensure exchange is updated too
                else:
                    # Create new record
                    new_record = EODData(trading_symbol=sym.trading_symbol, exchange=sym.exchange, date=today_date, open=float(ohlc.get("open", 0)), high=float(ohlc.get("high", 0)), low=float(ohlc.get("low", 0)), close=float(ohlc.get("close", 0)), volume=int(quote.get("volume", 0)), fo_eligible=sym.fo_eligible)
                    session.add(new_record)

                # Commit every 100 records to avoid large transactions
                if processed % 100 == 0:
                    try:
                        session.commit()
                    except SQLAlchemyError as e:
                        session.rollback()
                        log(f"[BATCH COMMIT ERROR] {segment} batch {batch_idx}, at record {processed}: {str(e)}")

                success_count += 1

            except (ValueError, TypeError, KeyError) as e:
                log(f"[DATA ERROR] {segment} batch {batch_idx}, ID {sec_id_str}: {str(e)}")
            except SQLAlchemyError as e:
                log(f"[DB ERROR] Processing {sym.trading_symbol if 'sym' in locals() else sec_id_str}: {str(e)}")
                # Continue processing other records

        # Final commit for remaining records
        try:
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            log(f"[FINAL COMMIT ERROR] {segment} batch {batch_idx}: {str(e)}")
            return f"[DB ERROR] {segment} batch {batch_idx}: {str(e)}"

        elapsed = time.time() - start_time
        return f"[OK] {segment} batch {batch_idx}/{total_batches} - Processed {processed}, inserted/updated {success_count} in {elapsed:.2f}s"

    except requests.exceptions.HTTPError as e:
        session.rollback()
        return f"[HTTP ERROR] {segment} batch {batch_idx}: {e}"
    except requests.exceptions.Timeout:
        session.rollback()
        return f"[TIMEOUT] {segment} batch {batch_idx}"
    except Exception as e:
        session.rollback()
        return f"[ERROR] {segment} batch {batch_idx}: {str(e)}"
    finally:
        session.close()


def fetch_today_eod_data(today_date: datetime.date, max_workers: int = 5):
    """Fetch today's EOD data for all active symbols."""
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

        # Group symbols by segment
        segment_to_ids = {}
        id_to_symbol = {}

        for sym in symbols:
            try:
                sid = int(sym.security_id)
                seg = sym.segment
                segment_to_ids.setdefault(seg, []).append(sid)
                id_to_symbol[sid] = sym
            except ValueError:
                log(f"[WARNING] Invalid security_id for {sym.trading_symbol}: {sym.security_id}")

        # Log summary
        log(f"[INFO] Fetching today's EOD data ({today_date}) for {len(symbols)} symbols across {len(segment_to_ids)} segments")

        # Process symbols in parallel
        futures = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for segment, sec_ids in segment_to_ids.items():
                chunks = list(split_list(sec_ids, 1000))  # API limit of 1000 symbols per request
                log(f"[INFO] Segment {segment}: {len(sec_ids)} symbols in {len(chunks)} batches")

                for idx, chunk in enumerate(chunks):
                    futures.append(executor.submit(fetch_batch, segment, chunk, idx + 1, len(chunks), today_date, id_to_symbol))

            # Process results
            successful, failed = 0, 0
            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                log(result)

                if result.startswith("[OK]"):
                    successful += 1
                elif result.startswith("[FAIL]") or result.startswith("[ERROR]") or result.startswith("[HTTP ERROR]"):
                    failed += 1

                # Progress update
                if (i + 1) % 5 == 0 or (i + 1) == len(futures):
                    elapsed = (datetime.now() - start_time).total_seconds()
                    remain = elapsed / (i + 1) * (len(futures) - i - 1)
                    log(f"[PROGRESS] {i+1}/{len(futures)} batches, Success: {successful}, Failed: {failed}, " f"Elapsed: {elapsed:.1f}s, Remaining: {remain:.1f}s")

        duration = (datetime.now() - start_time).total_seconds()
        log(f"✅ Today's candles fetched in {duration:.1f} seconds. Success: {successful}/{len(futures)} batches")

    except Exception as e:
        session.rollback()
        log(f"[ERROR] Failed to fetch today's data: {str(e)}")
    finally:
        session.close()


if __name__ == "__main__":
    today = datetime.now(tz=INDIA_TZ).date()
    fetch_today_eod_data(today_date=today)
