# scripts/import_symbol_master.py

import pandas as pd
import requests
from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from db.models.symbol import Symbol
from db.base_class import Base

# Constants
DHAN_SCRIP_MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"

# Step 1: Download and save the master CSV
def download_scrip_master():
    response = requests.get(DHAN_SCRIP_MASTER_URL)
    if response.status_code == 200:
        with open("api_scrip_master.csv", "wb") as f:
            f.write(response.content)
        print("[INFO] Scrip master downloaded successfully.")
    else:
        print("[ERROR] Failed to download scrip master.")
        exit(1)

# Step 2: Load, map, and insert symbols
def import_symbols():
    # Create tables if not already created
    Base.metadata.create_all(bind=engine)

    # Load full CSV
    df_full = pd.read_csv("api_scrip_master.csv")

    # Build Derivatives symbol list
    fo_symbols_list = df_full[(df_full['SEM_SEGMENT'] == 'D') &(df_full['SEM_EXCH_INSTRUMENT_TYPE'].isin(['FUTSTK', 'OPTSTK']))]['SEM_TRADING_SYMBOL'].tolist()

    # Filter only Equity stocks
    df = df_full[(df_full['SEM_SEGMENT'] == 'E') &(df_full['SEM_EXCH_INSTRUMENT_TYPE'] == 'ES')]

    mapped_records = []

    for _, row in df.iterrows():
        security_id = str(row.get('SEM_SMST_SECURITY_ID', ''))
        exchange = row.get('SEM_EXM_EXCH_ID', '')
        trading_symbol = row.get('SEM_TRADING_SYMBOL', '')
        name = row.get('SM_SYMBOL_NAME', '')
        instrument_type = "EQUITY"
        segment = f"{exchange}_EQ"

        # Convert lot_size safely to int
        try:
            lot_size_raw = row.get('SEM_LOT_UNITS', None)
            lot_size = int(lot_size_raw) if pd.notnull(lot_size_raw) else None
        except ValueError:
            lot_size = None

        active = True

        # Check F&O eligibility
        fo_eligible = any(derivative.startswith(trading_symbol + '-') for derivative in fo_symbols_list)

        # Create Symbol ORM object
        symbol_obj = Symbol(
            security_id=security_id,
            exchange=exchange,
            trading_symbol=trading_symbol,
            name=name,
            instrument_type=instrument_type,
            segment=segment,
            lot_size=lot_size,
            active=active,
            fo_eligible=fo_eligible
        )

        mapped_records.append(symbol_obj)

    # Insert into DB
    session: Session = SessionLocal()
    try:
        session.bulk_save_objects(mapped_records)
        session.commit()
        print(f"[INFO] Inserted {len(mapped_records)} symbols into the database.")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Failed to insert symbols: {e}")
    finally:
        session.close()

# Step 3: Run
if __name__ == "__main__":
    download_scrip_master()
    import_symbols()
