# scripts/ingest_eod_data.py

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models.eod_data import EODData
from scripts.fetch_eod_data import fetch_eod_data

def get_last_eod_date(session: Session) -> datetime.date:
    """Returns the last available date in eod_data table."""
    last_date = session.query(EODData.date).order_by(EODData.date.desc()).first()
    return last_date[0] if last_date else None

def ingest_eod_data():
    session: Session = SessionLocal()
    try:
        last_date = get_last_eod_date(session)
        today = datetime.now().date()

        if last_date is None:
            print("[INFO] No EOD data found. Will fetch full historical range using defaults.")
            fetch_eod_data()  # fallback to FROM_DATE, TO_DATE inside fetch script
            return

        from_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
        to_date = today.strftime("%Y-%m-%d")

        if from_date > to_date:
            print("[INFO] EOD data already up to date. No new data to fetch.")
            return

        print(f"[INFO] Ingesting EOD data from {from_date} to {to_date}...")
        fetch_eod_data(from_date=from_date, to_date=to_date)

    except Exception as e:
        print(f"[ERROR] Failed to ingest EOD data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    ingest_eod_data()
