# scripts/train_single_symbol.py

from core.train.daily_trainer import train_models_for_one_symbol
from core.config import RANDOM_FOREST

def main(symbol: str):
    train_models_for_one_symbol(symbol=symbol, move_classifiers=[RANDOM_FOREST], direction_classifiers=[RANDOM_FOREST])

if __name__ == "__main__":
    symbol = "ADANIENT"
    main(symbol)
