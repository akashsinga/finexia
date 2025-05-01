# scripts/fetch_eod_data.py

import time
import random
import threading
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from db.models.symbol import Symbol
from db.models.eod_data import EODData
from db.base_class import Base
from scripts.constants import DHAN_CHARTS_HISTORICAL_URL, INDIA_TZ, HEADERS, SAFE_SLEEP_BETWEEN_REQUESTS
from db.database import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
rate_limit_lock = threading.Semaphore(1)  # only 1 API request at a time

def log(msg): print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def fetch_eod_from_dhan(symbol: str, security_id: str, instrument_type: str, exchange_segment: str, from_date: str, to_date: str) -> dict:
    payload = {
        "securityId": str(security_id),
        "exchangeSegment": exchange_segment,
        "instrument": instrument_type,
        "expiryCode": 0,
        "oi": False,
        "fromDate": from_date,
        "toDate": to_date
    }

    for attempt in range(5):
        try:
            with rate_limit_lock:
                response = requests.post(DHAN_CHARTS_HISTORICAL_URL, headers=HEADERS, json=payload)
                time.sleep(SAFE_SLEEP_BETWEEN_REQUESTS + random.uniform(0.1, 0.5))  # Enforced global pacing
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "UNKNOWN"
            if status == 429:
                wait = (2 ** attempt) + random.uniform(0.1, 0.5)
                log(f"[RETRY] {symbol} hit 429. Waiting {wait:.1f}s...")
                time.sleep(wait)
            elif status == 403:
                log(f"[AUTH ERROR] {symbol} hit 403. Check credentials.")
                break
            elif status == 400:
                log(f"[BAD REQUEST] {symbol} hit 400. Likely invalid securityId/segment.")
                break
            else:
                log(f"[HTTP ERROR] {symbol}: {status} - {e}")
                break
        except Exception as e:
            log(f"[ERROR] Fetch failed for {symbol}: {e}")
            break

    return None

def create_eod_objects(symbol_dict, data, after_date: datetime.date):
    seen_dates = set()
    candles = []
    skipped_old = 0
    skipped_dupe = 0

    try:
        ts_list = data.get("timestamp", [])
        for i, ts in enumerate(ts_list):
            dt = datetime.fromtimestamp(ts, tz=INDIA_TZ).date()
            if dt <= after_date:
                skipped_old += 1
                continue
            if dt in seen_dates:
                skipped_dupe += 1
                continue

            seen_dates.add(dt)

            candles.append(EODData(
                trading_symbol=symbol_dict["trading_symbol"],
                exchange=symbol_dict["exchange"],
                date=dt,
                open=data["open"][i],
                high=data["high"][i],
                low=data["low"][i],
                close=data["close"][i],
                volume=int(data["volume"][i]),
                fo_eligible=symbol_dict["fo_eligible"]
            ))
    except Exception as e:
        log(f"[WARNING] Failed parsing {symbol_dict['trading_symbol']}: {e}")
    return candles, skipped_old, skipped_dupe

def fetch_and_insert_one_symbol(symbol_dict, from_date, to_date, last_date_lookup):
    session = SessionLocal()
    try:
        symbol = symbol_dict["trading_symbol"]
        after_date = last_date_lookup.get(symbol, datetime.strptime(from_date, "%Y-%m-%d").date())

        data = fetch_eod_from_dhan(
            symbol=symbol,
            security_id=symbol_dict["security_id"],
            instrument_type=symbol_dict["instrument_type"],
            exchange_segment=symbol_dict["segment"],
            from_date=after_date.strftime("%Y-%m-%d"),
            to_date=to_date
        )

        if data is None:
            return f"[FAIL] {symbol} - fetch failed"
        if "timestamp" not in data:
            return f"[SKIP] {symbol} - no candle data"

        candles, skip_old, skip_dup = create_eod_objects(symbol_dict, data, after_date)
        if not candles:
            return f"[SKIP] {symbol} - all old ({skip_old}) or dupes ({skip_dup})"

        session.bulk_save_objects(candles)
        session.commit()
        return f"[OK] {symbol} - inserted {len(candles)}, skipped: {skip_old} old, {skip_dup} dupes"

    except Exception as e:
        session.rollback()
        return f"[ERROR] {symbol_dict['trading_symbol']} failed: {e}"
    finally:
        session.close()

def fetch_eod_data(from_date: str, to_date: str, max_workers: int = 5):
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        symbols = session.query(Symbol).filter(Symbol.active == True).all()
        symbol_dicts = [{
            "security_id": str(s.security_id),
            "trading_symbol": s.trading_symbol,
            "exchange": s.exchange,
            "instrument_type": s.instrument_type,
            "segment": s.segment,
            "fo_eligible": s.fo_eligible
        } for s in symbols]

        log(f"[INFO] EOD fetch from {from_date} to {to_date} for {len(symbol_dicts)} symbols with {max_workers} threads.")

        last_dates = session.query(EODData.trading_symbol, func.max(EODData.date)).group_by(EODData.trading_symbol).all()
        last_date_lookup = {symbol: date for symbol, date in last_dates}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(fetch_and_insert_one_symbol, sym_dict, from_date, to_date, last_date_lookup)
                for sym_dict in symbol_dicts
            ]
            for f in as_completed(futures):
                log(f.result())

        log("✅ Rate-limited threaded EOD fetch complete.")

    except Exception as e:
        session.rollback()
        log(f"[ERROR] fetch_eod_data failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    from scripts.constants import FROM_DATE, TO_DATE
    fetch_eod_data(from_date=FROM_DATE, to_date=TO_DATE)
