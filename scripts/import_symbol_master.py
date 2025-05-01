# scripts/import_symbol_master.py

import pandas as pd
import requests
import hashlib
import json
import os
from io import StringIO
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.database import SessionLocal, engine
from db.models.symbol import Symbol
from db.base_class import Base
from scripts.constants import CACHE_DIR

# Constants
DHAN_SCRIP_MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"
CACHE_FILE = os.path.join(CACHE_DIR, "scrip_master_cache.csv")
CHECKSUM_FILE = os.path.join(CACHE_DIR, "scrip_master_checksum.txt")

def log(msg): print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def calculate_checksum(data: str) -> str:
    """Calculate MD5 checksum of data."""
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def download_and_parse_csv() -> pd.DataFrame:
    """Download and parse CSV with caching and validation."""
    try:
        # Download CSV
        response = requests.get(DHAN_SCRIP_MASTER_URL, timeout=60)
        if response.status_code != 200:
            raise Exception(f"Failed to download scrip master file. Status code: {response.status_code}")
        
        csv_text = response.text
        
        # Calculate checksum
        new_checksum = calculate_checksum(csv_text)
        
        # Check if we have a cached version
        if os.path.exists(CACHE_FILE) and os.path.exists(CHECKSUM_FILE):
            with open(CHECKSUM_FILE, 'r') as f:
                old_checksum = f.read().strip()
                
            if old_checksum == new_checksum:
                log("[INFO] Using cached scrip master file (unchanged)")
                return pd.read_csv(CACHE_FILE, low_memory=False)
        
        # Parse the CSV
        df = pd.read_csv(StringIO(csv_text), low_memory=False)
        
        # Validate data
        if df.empty:
            raise Exception("Downloaded CSV is empty")
            
        required_columns = ['SEM_SMST_SECURITY_ID', 'SEM_TRADING_SYMBOL', 'SEM_EXM_EXCH_ID', 
                           'SM_SYMBOL_NAME', 'SEM_SEGMENT', 'SEM_EXCH_INSTRUMENT_TYPE']
                           
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            raise Exception(f"CSV missing required columns: {', '.join(missing)}")
        
        # Cache the file and checksum
        os.makedirs(CACHE_DIR, exist_ok=True)
        df.to_csv(CACHE_FILE, index=False)
        with open(CHECKSUM_FILE, 'w') as f:
            f.write(new_checksum)
        
        log("[INFO] CSV downloaded and parsed successfully.")
        return df
        
    except requests.exceptions.RequestException as e:
        log(f"[ERROR] Request error: {e}")
        # If download fails but we have a cache, use it
        if os.path.exists(CACHE_FILE):
            log("[INFO] Download failed, using cached version")
            return pd.read_csv(CACHE_FILE, low_memory=False)
        raise
    except Exception as e:
        log(f"[ERROR] Failed to download/parse CSV: {e}")
        if os.path.exists(CACHE_FILE):
            log("[INFO] Error occurred, using cached version")
            return pd.read_csv(CACHE_FILE, low_memory=False)
        raise

def import_symbols():
    """Import symbols with change tracking and improved error handling."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    session: Session = SessionLocal()
    start_time = datetime.now()
    
    try:
        # Download and parse CSV
        df_full = download_and_parse_csv()

        # Identify derivatives symbols for F&O eligibility
        fo_symbols = df_full[
            (df_full['SEM_SEGMENT'] == 'D') & 
            (df_full['SEM_EXCH_INSTRUMENT_TYPE'].isin(['FUTSTK', 'OPTSTK']))
        ]['SEM_TRADING_SYMBOL'].unique().tolist()

        # Filter NSE EQ stocks
        df = df_full[
            (df_full['SEM_SEGMENT'] == 'E') & 
            (df_full['SEM_EXCH_INSTRUMENT_TYPE'] == 'ES') & 
            (df_full['SEM_EXM_EXCH_ID'] == 'NSE')
        ]

        log(f"[INFO] {len(df)} NSE EQ symbols found. Starting import...")

        # Get existing symbols for change tracking
        existing_symbols = {
            s.trading_symbol: {
                "security_id": s.security_id,
                "name": s.name,
                "segment": s.segment,
                "lot_size": s.lot_size,
                "fo_eligible": s.fo_eligible,
                "active": s.active
            }
            for s in session.query(Symbol).all()
        }

        added, updated, unchanged = 0, 0, 0
        changes = []

        # Process symbols
        for _, row in df.iterrows():
            trading_symbol = row['SEM_TRADING_SYMBOL']
            security_id = str(row.get('SEM_SMST_SECURITY_ID', '')).strip()
            exchange = row.get('SEM_EXM_EXCH_ID', '')
            name = row.get('SM_SYMBOL_NAME', '')
            instrument_type = "EQUITY"
            segment = f"{exchange}_EQ"
            lot_size = int(row['SEM_LOT_UNITS']) if pd.notnull(row['SEM_LOT_UNITS']) else None
            fo_eligible = any(derivative.startswith(trading_symbol + '-') for derivative in fo_symbols)

            # Check existing
            existing = session.query(Symbol).filter(
                Symbol.trading_symbol == trading_symbol, 
                Symbol.exchange == exchange
            ).first()
            
            if existing:
                # Check for changes
                changes_detected = False
                symbol_changes = {}
                
                if existing.security_id != security_id:
                    symbol_changes["security_id"] = {"old": existing.security_id, "new": security_id}
                    existing.security_id = security_id
                    changes_detected = True
                    
                if existing.name != name:
                    symbol_changes["name"] = {"old": existing.name, "new": name}
                    existing.name = name
                    changes_detected = True
                    
                if existing.segment != segment:
                    symbol_changes["segment"] = {"old": existing.segment, "new": segment}
                    existing.segment = segment
                    changes_detected = True
                    
                if existing.lot_size != lot_size:
                    symbol_changes["lot_size"] = {"old": existing.lot_size, "new": lot_size}
                    existing.lot_size = lot_size
                    changes_detected = True
                    
                if existing.fo_eligible != fo_eligible:
                    symbol_changes["fo_eligible"] = {"old": existing.fo_eligible, "new": fo_eligible}
                    existing.fo_eligible = fo_eligible
                    changes_detected = True
                    
                if not existing.active:
                    symbol_changes["active"] = {"old": existing.active, "new": True}
                    existing.active = True
                    changes_detected = True
                
                if changes_detected:
                    updated += 1
                    changes.append({
                        "symbol": trading_symbol,
                        "changes": symbol_changes
                    })
                else:
                    unchanged += 1
            else:
                # Add new symbol
                symbol_obj = Symbol(
                    security_id=security_id,
                    exchange=exchange,
                    trading_symbol=trading_symbol,
                    name=name,
                    instrument_type=instrument_type,
                    segment=segment,
                    lot_size=lot_size,
                    active=True,
                    fo_eligible=fo_eligible,
                )
                session.add(symbol_obj)
                added += 1
                changes.append({
                    "symbol": trading_symbol,
                    "action": "added"
                })

        # Mark missing symbols as inactive
        current_symbols = set(df['SEM_TRADING_SYMBOL'].unique())
        existing_active = set([s.trading_symbol for s in session.query(Symbol).filter(Symbol.active == True).all()])
        to_deactivate = existing_active - current_symbols
        
        if to_deactivate:
            deactivated = 0
            for symbol in to_deactivate:
                sym_obj = session.query(Symbol).filter(Symbol.trading_symbol == symbol).first()
                if sym_obj:
                    sym_obj.active = False
                    deactivated += 1
                    changes.append({"symbol": symbol,"action": "deactivated"})
            log(f"[INFO] Deactivated {deactivated} symbols no longer in master")

        # Save changes to database
        session.commit()
        
        # Write change log
        if changes:
            change_log_file = os.path.join(CACHE_DIR, f"symbol_changes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(change_log_file, 'w') as f:
                json.dump(changes, f, indent=2)
            log(f"[INFO] Change log saved to {change_log_file}")

        duration = (datetime.now() - start_time).total_seconds()
        log(f"[SUCCESS] Imported symbols in {duration:.1f}s - Added: {added}, Updated: {updated}, Unchanged: {unchanged}")

    except Exception as e:
        session.rollback()
        log(f"[ERROR] Symbol import failed: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    import_symbols()
