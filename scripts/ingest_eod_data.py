# scripts/ingest_eod_data.py

from scripts.fetch_eod_data import fetch_eod_data
from scripts.fetch_today_eod import fetch_today_eod_data
from db.models.eod_data import EODData
from db.models.symbol import Symbol
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.database import SessionLocal
from datetime import datetime, timedelta
import time

def log(msg): print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

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
    query = session.query(EODData.trading_symbol, func.max(EODData.date).label('last_date'))
    
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
    count = session.query(func.count(EODData.id)).filter(
        EODData.trading_symbol.in_(symbol_list),
        EODData.date == today
    ).scalar()
    
    # If we have at least half of the symbols, consider it present
    return count >= len(symbol_list) / 2

def is_market_closed() -> bool:
    """Check if market is closed based on time of day."""
    now = datetime.now()
    # Market closes at 3:30 PM IST
    return now.hour >= 15 and now.minute >= 30

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
            next_date = last_date + timedelta(days=1)
            log(f"[INFO] Last EOD date in database: {last_date}")
            
            # Check for gaps
            if next_date < today:
                # Calculate number of days to fetch
                days_to_fetch = (today - next_date).days
                
                if days_to_fetch > 30:
                    # For large gaps, fetch in chunks to avoid timeouts
                    log(f"[INFO] Large gap detected ({days_to_fetch} days). Fetching in chunks...")
                    chunk_size = 30  # days
                    current_from = next_date
                    
                    while current_from < today:
                        current_to = min(current_from + timedelta(days=chunk_size - 1), today - timedelta(days=1))
                        log(f"[INFO] Fetching chunk from {current_from} to {current_to}")
                        
                        fetch_eod_data(
                            from_date=current_from.strftime("%Y-%m-%d"), 
                            to_date=current_to.strftime("%Y-%m-%d")
                        )
                        
                        # Small pause between chunks
                        time.sleep(5)
                        current_from = current_to + timedelta(days=1)
                else:
                    # For smaller gaps, fetch in one go
                    log(f"[INFO] Fetching historical gap from {next_date} to {today - timedelta(days=1)}")
                    fetch_eod_data(
                        from_date=next_date.strftime("%Y-%m-%d"), 
                        to_date=(today - timedelta(days=1)).strftime("%Y-%m-%d")
                    )
            else:
                log("[INFO] No historical gap to fill.")

        # Only fetch today's data if it's post market close and not already present
        if is_market_closed():
            if not is_today_data_present(session, today):
                log(f"[INFO] Fetching today's EOD data for {today}")
                fetch_today_eod_data(today_date=today)
            else:
                log("[INFO] Today's data already present.")
        else:
            log("[INFO] Market still open or today's data already present. Skipping today's data fetch.")

        # Check data quality 
        active_symbol_count = session.query(func.count(Symbol.id)).filter(Symbol.active == True).scalar()
        today_data_count = session.query(func.count(EODData.id)).filter(EODData.date == today).scalar()
        
        if is_market_closed() and today_data_count < active_symbol_count * 0.7:  # Less than 70% coverage
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
