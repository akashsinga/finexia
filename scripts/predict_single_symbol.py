# scripts/predict_single_symbol.py

from core.predict.daily_predictor import predict_for_one_symbol

def main(symbol: str):
    predict_for_one_symbol(symbol)

if __name__ == "__main__":
    symbol = "ADANIENT"
    main(symbol)
