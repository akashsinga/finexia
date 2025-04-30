# scripts/parallel_train_predict.py

from concurrent.futures import ProcessPoolExecutor, as_completed
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models.symbol import Symbol
from core.train.daily_trainer import train_models_for_one_symbol
from core.predict.daily_predictor import predict_for_one_symbol
from core.config import RANDOM_FOREST
from datetime import datetime

def train_and_predict(symbol: str) -> str:
    try:
        # Train
        train_models_for_one_symbol(symbol=symbol,move_classifiers=[RANDOM_FOREST],direction_classifiers=[RANDOM_FOREST])

        # Predict
        predict_for_one_symbol(symbol=symbol)

        return f"[✅] {symbol}: Trained + Predicted"

    except Exception as e:
        return f"[❌] {symbol}: Failed - {e}"

def run_parallel_train_predict(max_workers: int = 8):
    session: Session = SessionLocal()
    try:
        symbols = session.query(Symbol.trading_symbol).filter(Symbol.active == True).all()
        symbol_list = [s.trading_symbol for s in symbols]

        print(f"[INFO] Running parallel training + prediction for {len(symbol_list)} symbols with {max_workers} workers...")

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(train_and_predict, symbol): symbol for symbol in symbol_list}

            for future in as_completed(futures):
                print(future.result())

    finally:
        session.close()
