# core/features/feature_engineer.py

import pandas as pd
import numpy as np

def calculate_features(eod_df: pd.DataFrame, symbol_df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes raw EOD candle data and symbol master data, returns dataframe with 10 core features calculated.
    """
    df = eod_df.copy()
    df = df.sort_values(["trading_symbol", "date"]).reset_index(drop=True)

    # Basic calculations
    df["hl_range"] = (df["high"] - df["low"]) / df["close"]
    df["gap_pct"] = (df["open"] / df.groupby("trading_symbol")["close"].shift(1)) - 1
    df["body_to_range_ratio"] = (df["close"] - df["open"]).abs() / (df["high"] - df["low"]).replace(0, np.nan)

    # Trend and momentum
    df["distance_from_ema_5"] = df.groupby("trading_symbol")["close"].transform(lambda x: x.ewm(span=5, adjust=False).mean())
    df["distance_from_ema_5"] = df["close"] - df["distance_from_ema_5"]
    df["return_3d"] = df.groupby("trading_symbol")["close"].pct_change(periods=3)
    df["range_compression_ratio"] = df["hl_range"] / df.groupby("trading_symbol")["hl_range"].transform(lambda x: x.rolling(3).mean())

    # ATR-like volatility
    df["atr_5"] = df.groupby("trading_symbol")["hl_range"].transform(lambda x: x.rolling(5).mean())

    # Volume and volatility compression
    df["volume_spike_ratio"] = df["volume"] / df.groupby("trading_symbol")["volume"].transform(lambda x: x.rolling(3).mean())
    
    rolling_mean = df.groupby("trading_symbol")["close"].transform(lambda x: x.rolling(20).mean())
    rolling_std = df.groupby("trading_symbol")["close"].transform(lambda x: x.rolling(20).std())
    upper_bb = rolling_mean + (2 * rolling_std)
    lower_bb = rolling_mean - (2 * rolling_std)
    bb_width = (upper_bb - lower_bb) / rolling_mean
    df["volatility_squeeze"] = bb_width / bb_width.rolling(20).mean()

    # Trend zone strength
    up_move = df.groupby("trading_symbol")["high"].diff()
    down_move = df.groupby("trading_symbol")["low"].diff().abs()
    dm = np.where(up_move > down_move, up_move, 0)
    df["trend_zone_strength"] = pd.Series(dm).rolling(14).mean()

    # Add FO Eligible (ignored in training but necessary for database integrity)
    symbol_map = symbol_df.set_index("trading_symbol")["fo_eligible"].to_dict()
    df["fo_eligible"] = df["trading_symbol"].map(symbol_map).fillna(False)

    # Final features to select
    features_cols = [
        "trading_symbol", "exchange", "date",
        "volatility_squeeze",
        "trend_zone_strength",
        "range_compression_ratio",
        "volume_spike_ratio",
        "body_to_range_ratio",
        "distance_from_ema_5",
        "gap_pct",
        "return_3d",
        "atr_5",
        "hl_range",
        "fo_eligible"  # (optional, not used in training but kept for integrity)
    ]

    return df[features_cols]
