# scripts/import_symbol_master.py

import pandas as pd
import requests
from io import StringIO
from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from db.models.symbol import Symbol
from db.base_class import Base

# Constants
DHAN_SCRIP_MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"

def download_and_parse_csv() -> pd.DataFrame:
    response = requests.get(DHAN_SCRIP_MASTER_URL)
    if response.status_code != 200:
        raise Exception("Failed to download scrip master file.")
    
    print("[INFO] CSV downloaded successfully.")
    return pd.read_csv(StringIO(response.text), low_memory=False)

def import_symbols():
    Base.metadata.create_all(bind=engine)
    session: Session = SessionLocal()

    try:
        df_full = download_and_parse_csv()

        # Derivatives list for F&O eligibility
        fo_symbols = df_full[(df_full['SEM_SEGMENT'] == 'D') &(df_full['SEM_EXCH_INSTRUMENT_TYPE'].isin(['FUTSTK', 'OPTSTK']))]['SEM_TRADING_SYMBOL'].tolist()

        # Filter NSE EQ stocks
        df = df_full[(df_full['SEM_SEGMENT'] == 'E') &(df_full['SEM_EXCH_INSTRUMENT_TYPE'] == 'ES') &(df_full['SEM_EXM_EXCH_ID'] == 'NSE')]

        print(f"[INFO] {len(df)} NSE EQ symbols found. Starting import...")

        added, updated = 0, 0

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
            existing = session.query(Symbol).filter(Symbol.trading_symbol == trading_symbol, Symbol.exchange == exchange).first()
            if existing:
                existing.security_id = security_id
                existing.name = name
                existing.segment = segment
                existing.lot_size = lot_size
                existing.active = True
                existing.fo_eligible = fo_eligible
                updated += 1
            else:
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

        session.commit()
        print(f"[SUCCESS] Imported symbols - Added: {added}, Updated: {updated}")

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Symbol import failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    import_symbols()
