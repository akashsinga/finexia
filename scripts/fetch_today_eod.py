# scripts/fetch_today_eod.py

import time
import random
import threading
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from db.models.symbol import Symbol
from db.models.eod_data import EODData
from db.base_class import Base
from scripts.constants import DHAN_TODAY_EOD_URL, HEADERS, INDIA_TZ, SAFE_SLEEP_BETWEEN_REQUESTS

rate_limit_lock = threading.Semaphore(1)

def log(msg): print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def split_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def fetch_batch(segment: str, chunk: list[int], batch_idx: int, total_batches: int, today_date: datetime.date, id_to_symbol: dict) -> str:
    session: Session = SessionLocal()
    try:
        payload = {segment: chunk}
        with rate_limit_lock:
            response = requests.post(DHAN_TODAY_EOD_URL, headers=HEADERS, json=payload)
            time.sleep(SAFE_SLEEP_BETWEEN_REQUESTS + random.uniform(0.1, 0.5))
        response.raise_for_status()

        result = response.json()
        data = result.get("data", {}).get(segment, {})

        candles = []
        for sec_id_str, quote in data.items():
            sid = int(sec_id_str)
            sym = id_to_symbol.get(sid)
            if not sym:
                continue

            ohlc = quote.get("ohlc", {})
            candle = EODData(
                trading_symbol=sym.trading_symbol,
                exchange=sym.exchange,
                date=today_date,
                open=ohlc.get("open", 0),
                high=ohlc.get("high", 0),
                low=ohlc.get("low", 0),
                close=ohlc.get("close", 0),
                volume=int(quote.get("volume", 0)),
                fo_eligible=sym.fo_eligible
            )
            candles.append(candle)

        if candles:
            for c in candles:
                session.merge(c)
            session.commit()
        return f"[OK] {segment} batch {batch_idx}/{total_batches} - inserted {len(candles)}"

    except requests.exceptions.HTTPError as e:
        return f"[HTTP ERROR] {segment} batch {batch_idx}: {e}"
    except Exception as e:
        session.rollback()
        return f"[ERROR] {segment} batch {batch_idx}: {e}"
    finally:
        session.close()

def fetch_today_eod_data(today_date: datetime.date, max_workers: int = 5):
    Base.metadata.create_all(bind=engine)
    session: Session = SessionLocal()

    try:
        symbols = session.query(Symbol).filter(Symbol.active == True).all()
        if not symbols:
            log("[WARNING] No active symbols found.")
            return

        segment_to_ids = {}
        id_to_symbol = {}

        for sym in symbols:
            sid = int(sym.security_id)
            seg = sym.segment
            segment_to_ids.setdefault(seg, []).append(sid)
            id_to_symbol[sid] = sym

        futures = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for segment, sec_ids in segment_to_ids.items():
                chunks = list(split_list(sec_ids, 1000))
                for idx, chunk in enumerate(chunks):
                    futures.append(
                        executor.submit(
                            fetch_batch,
                            segment, chunk, idx + 1, len(chunks), today_date, id_to_symbol
                        )
                    )

            for f in as_completed(futures):
                log(f.result())

        log(f"✅ Today's candles inserted using threaded + rate-limited fetch.")

    except Exception as e:
        session.rollback()
        log(f"[ERROR] Failed to fetch today's data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    today = datetime.now(tz=INDIA_TZ).date()
    fetch_today_eod_data(today_date=today)
