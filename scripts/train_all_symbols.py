# scripts/train_all_symbols.py

from core.train.daily_trainer import train_daily_model
from core.config import RANDOM_FOREST

def main():
    train_daily_model(move_classifiers=[RANDOM_FOREST], direction_classifiers=[RANDOM_FOREST])

if __name__ == "__main__":
    main()
