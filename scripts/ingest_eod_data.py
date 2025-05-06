# scripts/ingest_eod_data.py

from scripts.fetch_eod_data import fetch_eod_data
from scripts.fetch_today_eod import fetch_today_eod_data
from db.models.eod_data import EODData
from db.models.symbol import Symbol
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.database import SessionLocal
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def get_last_eod_date(session: Session):
    """Get the last EOD date in the database with error handling."""
    try:
        last = session.query(func.max(EODData.date)).first()
        return last[0] if last and last[0] else None
    except Exception as e:
        log(f"[ERROR] Failed to get last EOD date: {str(e)}")
        return None


def get_symbol_last_dates(session: Session, trading_symbols=None):
    """Get last EOD date for each symbol for more targeted updates."""
    query = session.query(EODData.trading_symbol, func.max(EODData.date).label("last_date"))

    if trading_symbols:
        query = query.filter(EODData.trading_symbol.in_(trading_symbols))

    return {row.trading_symbol: row.last_date for row in query.group_by(EODData.trading_symbol).all()}


def is_today_data_present(session: Session, today: datetime.date) -> bool:
    """Check if today's data is already present with sampling."""
    # Check a sample of active symbols
    active_symbols = session.query(Symbol.trading_symbol).filter(Symbol.active == True).limit(10).all()
    symbol_list = [s.trading_symbol for s in active_symbols]

    if not symbol_list:
        return False

    # Count records for today
    count = session.query(func.count(EODData.id)).filter(EODData.trading_symbol.in_(symbol_list), EODData.date == today).scalar()

    # If we have at least half of the symbols, consider it present
    return count >= len(symbol_list) / 2


def is_market_closed() -> bool:
    """Check if market is closed based on time of day."""
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    print("IST Time:", now)
    return now.hour > 15 or (now.hour == 15 and now.minute >= 30)


def is_weekend(date: datetime.date) -> bool:
    """Check if the given date is a weekend."""
    return date.weekday() >= 5  # 5=Saturday, 6=Sunday


def is_holiday(date: datetime.date) -> bool:
    """Check if the given date is a holiday."""
    # Common Indian market holidays for 2025
    holidays_2025 = [
        datetime(2025, 1, 1).date(),  # New Year's Day
        datetime(2025, 1, 26).date(),  # Republic Day
        datetime(2025, 3, 2).date(),  # Mahashivratri
        datetime(2025, 3, 17).date(),  # Holi
        datetime(2025, 4, 14).date(),  # Dr. Ambedkar Jayanti
        datetime(2025, 4, 18).date(),  # Good Friday
        datetime(2025, 5, 1).date(),  # Maharashtra Day
        datetime(2025, 8, 15).date(),  # Independence Day
        datetime(2025, 9, 2).date(),  # Ganesh Chaturthi
        datetime(2025, 10, 2).date(),  # Gandhi Jayanti
        datetime(2025, 10, 23).date(),  # Dussehra
        datetime(2025, 11, 12).date(),  # Diwali
        datetime(2025, 11, 14).date(),  # Diwali (Balipratipada)
        datetime(2025, 12, 25).date(),  # Christmas
    ]

    return date in holidays_2025


def is_trading_day(date: datetime.date) -> bool:
    """Check if the given date is a trading day (not weekend or holiday)."""
    return not (is_weekend(date) or is_holiday(date))


def get_next_trading_day(date: datetime.date) -> datetime.date:
    """Get the next trading day after the given date."""
    next_date = date + timedelta(days=1)
    while not is_trading_day(next_date):
        next_date = next_date + timedelta(days=1)
    return next_date


def ingest_eod_data():
    """Ingest EOD data with improved gap detection and recovery."""
    session = SessionLocal()
    start_time = datetime.now()

    try:
        today = datetime.now().date()
        log(f"[INFO] Starting EOD data ingestion on {today}...")

        # Get last date in database
        last_date = get_last_eod_date(session)

        if last_date is None:
            log("[INFO] No historical EOD data found. Fetching all...")
            from scripts.constants import FROM_DATE, TO_DATE

            fetch_eod_data(from_date=FROM_DATE, to_date=TO_DATE)
        else:
            # Find the next trading day after the last recorded date
            next_date = get_next_trading_day(last_date)
            log(f"[INFO] Last EOD date in database: {last_date}")
            log(f"[INFO] Next trading day to fetch: {next_date}")

            # Check for gaps
            if next_date < today:
                # Calculate number of trading days to fetch
                trading_days_to_fetch = 0
                temp_date = next_date
                while temp_date < today:
                    if is_trading_day(temp_date):
                        trading_days_to_fetch += 1
                    temp_date = temp_date + timedelta(days=1)

                log(f"[INFO] Gap detected: {(today - next_date).days} calendar days, {trading_days_to_fetch} trading days")

                if trading_days_to_fetch == 0:
                    log("[INFO] No trading days in the gap, nothing to fetch.")
                else:
                    if (today - next_date).days > 30:
                        # For large gaps, fetch in chunks to avoid timeouts
                        log(f"[INFO] Large gap detected. Fetching in chunks...")
                        chunk_size = 30  # days
                        current_from = next_date

                        while current_from < today:
                            # Find the end date for this chunk
                            current_to = current_from
                            days_in_chunk = 0
                            while days_in_chunk < chunk_size and current_to < today - timedelta(days=1):
                                next_to = current_to + timedelta(days=1)
                                if is_trading_day(next_to):
                                    days_in_chunk += 1
                                current_to = next_to

                            log(f"[INFO] Fetching chunk from {current_from} to {current_to}")

                            fetch_eod_data(from_date=current_from.strftime("%Y-%m-%d"), to_date=current_to.strftime("%Y-%m-%d"))

                            # Small pause between chunks
                            time.sleep(5)
                            current_from = get_next_trading_day(current_to)
                    else:
                        # For smaller gaps, fetch in one go
                        yesterday = today - timedelta(days=1)
                        # If yesterday was not a trading day, find the last trading day
                        while not is_trading_day(yesterday) and yesterday > next_date:
                            yesterday = yesterday - timedelta(days=1)

                        log(f"[INFO] Fetching historical gap from {next_date} to {yesterday}")
                        fetch_eod_data(from_date=next_date.strftime("%Y-%m-%d"), to_date=yesterday.strftime("%Y-%m-%d"))
            else:
                log("[INFO] No historical gap to fill.")

        # Check if today is a trading day
        is_today_trading = is_trading_day(today)
        log(f"[INFO] Is today ({today}) a trading day? {is_today_trading}")

        # Check if market is closed
        market_closed = is_market_closed()
        log(f"[INFO] Is market closed? {market_closed}")

        # Check if today's data is present
        today_data_exists = is_today_data_present(session, today)
        log(f"[INFO] Is today's data already present? {today_data_exists}")

        # Only fetch today's data if it's a trading day, market is closed, and data not present yet
        if is_today_trading and market_closed and not today_data_exists:
            log(f"[INFO] Fetching today's EOD data for {today}")
            fetch_today_eod_data(today_date=today)
        else:
            if not is_today_trading:
                log("[INFO] Today is not a trading day. Skipping today's data fetch.")
            elif not market_closed:
                log("[INFO] Market still open. Skipping today's data fetch.")
            else:
                log("[INFO] Today's data already present. Skipping today's data fetch.")

        # Check data quality
        active_symbol_count = session.query(func.count(Symbol.id)).filter(Symbol.active == True).scalar()
        if is_today_trading:
            today_data_count = session.query(func.count(EODData.id)).filter(EODData.date == today).scalar()

            log(f"[INFO] Today's data count: {today_data_count} out of {active_symbol_count} active symbols")
            if market_closed and today_data_count < active_symbol_count * 0.7:  # Less than 70% coverage
                log(f"[WARNING] Today's data may be incomplete. Expected: ~{active_symbol_count}, Got: {today_data_count}")

        # Log summary
        total_records = session.query(func.count(EODData.id)).scalar()
        date_range = session.query(func.min(EODData.date), func.max(EODData.date)).first()

        duration = (datetime.now() - start_time).total_seconds()
        log(f"[SUCCESS] EOD data ingestion completed in {duration:.1f} seconds.")
        log(f"[INFO] Database now contains {total_records} records from {date_range[0]} to {date_range[1]}")

    except Exception as e:
        log(f"[ERROR] Failed to ingest EOD data: {str(e)}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    ingest_eod_data()
