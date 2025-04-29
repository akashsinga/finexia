# scripts/ingest_eod_data.py

import os
import time
import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from db.models.eod_data import EODData
from db.models.symbol import Symbol
from db.base_class import Base
from scripts.fetch_eod_data import fetch_eod_data
from scripts.constants import DHAN_TODAY_EOD_URL, HEADERS

def get_last_eod_date(session: Session) -> datetime.date:
    """Returns the last available date in eod_data table."""
    last_date = session.query(EODData.date).order_by(EODData.date.desc()).first()
    return last_date[0] if last_date else None

def is_today_data_present(session: Session, today: datetime.date) -> bool:
    """Check if today's data already exists in EODData."""
    today_data = session.query(EODData).filter(EODData.date == today).first()
    return today_data is not None

def split_list_into_chunks(lst, chunk_size):
    """Splits a list into smaller lists of given chunk size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def fetch_today_eod_data(session: Session, today: datetime.date):
    """Fetch and insert today's EOD candles using today's API."""
    print("[INFO] Fetching today's EOD data using today's API...")

    Base.metadata.create_all(bind=engine)
    symbols = session.query(Symbol).filter(Symbol.active == True).all()
    if not symbols:
        print("[WARNING] No active symbols found.")
        return

    segment_to_ids = {}
    security_id_to_symbol = {}

    for sym in symbols:
        seg = sym.segment
        segment_to_ids.setdefault(seg, []).append(int(sym.security_id))  # force int
        security_id_to_symbol[int(sym.security_id)] = sym

    inserted_count = 0

    for segment, sec_ids in segment_to_ids.items():
        chunks = list(split_list_into_chunks(sec_ids, 1000))

        for idx, chunk in enumerate(chunks):
            payload = {segment: chunk}
            headers = HEADERS.copy()

            try:
                print(f"[INFO] Fetching {len(chunk)} symbols from {segment}, batch {idx+1}/{len(chunks)}...")
                response = requests.post(DHAN_TODAY_EOD_URL, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                segment_data = result.get("data", {}).get(segment, {})

                for sec_id_str, data in segment_data.items():
                    sec_id = int(sec_id_str)
                    sym = security_id_to_symbol.get(sec_id)

                    if sym is None:
                        continue  # safe guard

                    ohlc = data.get("ohlc", {})
                    candle = EODData(
                        trading_symbol=sym.trading_symbol,
                        exchange=sym.exchange,
                        date=today,
                        open=ohlc.get("open", 0),
                        high=ohlc.get("high", 0),
                        low=ohlc.get("low", 0),
                        close=ohlc.get("close", 0),
                        volume=int(data.get("volume", 0)),
                        fo_eligible=sym.fo_eligible
                    )

                    session.merge(candle)
                    inserted_count += 1

            except Exception as e:
                print(f"[ERROR] Failed to fetch/insert for segment {segment}, batch {idx+1}: {e}")
                print(f"[DEBUG] Payload sent: {payload}")
                print(f"[DEBUG] Headers used: {headers}")

            time.sleep(1)  # throttle between API calls

    session.commit()
    print(f"[INFO] Inserted today's EOD candles for {inserted_count} symbols.")

def ingest_eod_data():
    session: Session = SessionLocal()
    try:
        last_date = get_last_eod_date(session)
        today = datetime.now().date()

        if last_date is None:
            print("[INFO] No EOD data found. Fetching full historical range.")
            fetch_eod_data()
        else:
            from_date_dt = last_date + timedelta(days=1)
            to_date_dt = today

            if from_date_dt < to_date_dt:
                from_date = from_date_dt.strftime("%Y-%m-%d")
                to_date = (to_date_dt - timedelta(days=1)).strftime("%Y-%m-%d")
                print(f"[INFO] Ingesting historical EOD data from {from_date} to {to_date}...")
                fetch_eod_data(from_date=from_date, to_date=to_date)
            else:
                print("[INFO] No new historical data needed.")

        # Fetch today's candle separately if not present and it's after 3:30 PM
        if datetime.now().hour >= 15 and not is_today_data_present(session, today):
            fetch_today_eod_data(session, today)
        else:
            print("[INFO] Today's EOD data already present or not yet ready.")

    except Exception as e:
        print(f"[ERROR] Failed to ingest EOD data: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    ingest_eod_data()
