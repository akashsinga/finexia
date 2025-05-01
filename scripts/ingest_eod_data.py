# scripts/ingest_eod_data.py

from scripts.fetch_eod_data import fetch_eod_data
from scripts.fetch_today_eod import fetch_today_eod_data
from db.models.eod_data import EODData
from sqlalchemy.orm import Session
from db.database import SessionLocal
from datetime import datetime, timedelta

def log(msg): print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def get_last_eod_date(session: Session):
    last = session.query(EODData.date).order_by(EODData.date.desc()).first()
    return last[0] if last else None

def is_today_data_present(session: Session, today: datetime.date) -> bool:
    return session.query(EODData).filter(EODData.date == today).first() is not None

def ingest_eod_data():
    session = SessionLocal()
    try:
        today = datetime.now().date()
        last_date = get_last_eod_date(session)

        if last_date is None:
            log("[INFO] No historical EOD data found. Fetching all...")
            from scripts.constants import FROM_DATE, TO_DATE
            fetch_eod_data(from_date=FROM_DATE, to_date=TO_DATE)
        else:
            next_date = last_date + timedelta(days=1)
            if next_date < today:
                log(f"[INFO] Fetching historical gap from {next_date} to {today - timedelta(days=1)}")
                fetch_eod_data(from_date=next_date.strftime("%Y-%m-%d"), to_date=(today - timedelta(days=1)).strftime("%Y-%m-%d"))
            else:
                log("[INFO] No historical gap to fill.")

        # Only fetch today’s data if it’s post 3:30 PM and not already present
        if datetime.now().hour >= 15 and not is_today_data_present(session, today):
            fetch_today_eod_data(today_date=today)
        else:
            log("[INFO] Today's data already present or not ready yet.")

    except Exception as e:
        log(f"[ERROR] Failed to ingest EOD data: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    ingest_eod_data()
