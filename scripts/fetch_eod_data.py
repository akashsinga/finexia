# scripts/fetch_eod_data.py

import time
import requests
from sqlalchemy.orm import Session
from datetime import datetime
from db.database import SessionLocal, engine
from db.models.symbol import Symbol
from db.models.eod_data import EODData
from db.base_class import Base
from scripts.constants import (DHAN_CHARTS_HISTORICAL_URL, FROM_DATE, TO_DATE,INDIA_TZ, HEADERS, SAFE_SLEEP_BETWEEN_REQUESTS)


def fetch_eod_from_dhan(security_id: str, instrument_type: str, exchange_segment: str) -> dict:
    """Fetch historical EOD data from Dhan API for a given security."""
    payload = {
        "securityId": security_id,
        "exchangeSegment": exchange_segment,
        "instrument": instrument_type,
        "expiryCode": 0,
        "oi": False,
        "fromDate": FROM_DATE,
        "toDate": TO_DATE
    }
    
    print("[DEBUG] Payload: ", payload)
    
    try:
        response = requests.post(DHAN_CHARTS_HISTORICAL_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP Error: {e}")
        print(f"[ERROR] Response Text: {response.text}")
        return {}
    except Exception as e:
        print(f"[ERROR] Failed to fetch for securityId {security_id} ({exchange_segment}): {e}")
        return {}

def create_candle_objects(trading_symbol: str, exchange: str, fo_eligible: bool, data: dict) -> list:
    """Create a list of EODData ORM objects from raw candle data."""
    candles = []
    try:
        for i in range(len(data['timestamp'])):
            candle = EODData(
                trading_symbol=trading_symbol,
                exchange=exchange,
                date=datetime.fromtimestamp(data['timestamp'][i], tz=INDIA_TZ).date(),
                open=data['open'][i],
                high=data['high'][i],
                low=data['low'][i],
                close=data['close'][i],
                volume=int(data['volume'][i]),
                fo_eligible=fo_eligible
            )
            candles.append(candle)
    except Exception as e:
        print(f"[WARNING] Failed to parse candle for {trading_symbol}: {e}")
    return candles

def fetch_eod_data():
    """Fetch, create candles, and insert EOD data for all active NSE symbols (optimized with duplicate logging)."""
    Base.metadata.create_all(bind=engine)
    session: Session = SessionLocal()

    symbols = session.query(Symbol).filter(Symbol.active == True).all()
    print(f"[INFO] Fetching EOD data for {len(symbols)} NSE symbols...")

    for sym in symbols:
        security_id = sym.security_id
        trading_symbol = sym.trading_symbol
        exchange_segment = sym.segment
        fo_eligible = sym.fo_eligible

        print(f"[INFO] Fetching for {trading_symbol} ({exchange_segment})...")

        data = fetch_eod_from_dhan(security_id, sym.instrument_type, exchange_segment)

        if not data or 'timestamp' not in data:
            print(f"[WARNING] No data returned for {trading_symbol} ({exchange_segment})")
            continue

        candles = create_candle_objects(trading_symbol, sym.exchange, fo_eligible, data)

        if not candles:
            print(f"[WARNING] No valid candles created for {trading_symbol} ({exchange_segment})")
            continue

        # Deduplicate candles based on date (in-memory)
        seen_dates = set()
        unique_candles = []
        for candle in candles:
            if candle.date not in seen_dates:
                unique_candles.append(candle)
                seen_dates.add(candle.date)

        if len(candles) != len(unique_candles):
            print(f"[INFO] {len(candles) - len(unique_candles)} duplicate candles removed for {trading_symbol}.")

        if unique_candles:
            try:
                session.bulk_save_objects(unique_candles)
                session.commit()
                print(f"[INFO] Inserted {len(unique_candles)} candles for {trading_symbol} successfully.")
            except Exception as e:
                session.rollback()
                print(f"[ERROR] Failed to insert candles for {trading_symbol}: {e}")
        else:
            print(f"[WARNING] No unique candles to insert for {trading_symbol}")

        time.sleep(SAFE_SLEEP_BETWEEN_REQUESTS)

    session.close()
    print(f"[INFO] Full EOD data fetching and insertion completed.")



if __name__ == "__main__":
    fetch_eod_data()
