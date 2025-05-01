# scripts/train_symbol_runner.py

import argparse
from core.train.symbol_trainer import train_symbol_model
from core.config import LIGHTGBM

def main():
    parser = argparse.ArgumentParser(description="Train models for a single symbol with configurable parameters.")
    parser.add_argument("--symbol", required=True, help="Trading symbol to train")
    parser.add_argument("--threshold", type=float, default=8.0)
    parser.add_argument("--min-days", type=int, default=1)
    parser.add_argument("--max-days", type=int, default=10)
    parser.add_argument("--move-models", nargs="+", default=[LIGHTGBM])
    parser.add_argument("--direction-models", nargs="+", default=[LIGHTGBM])
    args = parser.parse_args()

    train_symbol_model(symbol=args.symbol,move_classifiers=args.move_models,direction_classifiers=args.direction_models,threshold_percent=args.threshold,min_days=args.min_days,max_days=args.max_days)

if __name__ == "__main__":
    main()
