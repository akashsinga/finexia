# core/features/feature_engineer.py

import pandas as pd
import numpy as np

def calculate_features(eod_df: pd.DataFrame, symbol_df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes raw EOD candle data and symbol master data, returns dataframe with features calculated.
    """
    df = eod_df.copy()
    df = df.sort_values(["trading_symbol", "date"]).reset_index(drop=True)

    # Basic calculations
    df["hl_range"] = (df["high"] - df["low"]) / df["close"]
    df["price_change_t_1"] = df.groupby("trading_symbol")["close"].pct_change()
    df["gap_pct"] = df["open"] / df.groupby("trading_symbol")["close"].shift(1) - 1
    df["body_to_range_ratio"] = (df["close"] - df["open"]).abs() / (df["high"] - df["low"]).replace(0, np.nan)

    # Wick percentages
    df["lower_wick_pct"] = (np.minimum(df["open"], df["close"]) - df["low"]) / df["close"]
    df["upper_wick_pct"] = (df["high"] - np.maximum(df["open"], df["close"])) / df["close"]

    # Closing strength
    df["closing_strength"] = (df["close"] - df["low"]) / (df["high"] - df["low"]).replace(0, np.nan)

    # Trend and momentum
    df["distance_from_ema_5"] = df.groupby("trading_symbol")["close"].transform(lambda x: x.ewm(span=5, adjust=False).mean())
    df["distance_from_ema_5"] = df["close"] - df["distance_from_ema_5"]

    df["return_3d"] = df.groupby("trading_symbol")["close"].pct_change(periods=3)
    df["return_5d"] = df.groupby("trading_symbol")["close"].pct_change(periods=5)

    high_5d = df.groupby("trading_symbol")["high"].transform(lambda x: x.rolling(5).max())
    low_5d = df.groupby("trading_symbol")["low"].transform(lambda x: x.rolling(5).min())
    df["position_in_range_5d"] = (df["close"] - low_5d) / (high_5d - low_5d).replace(0, np.nan)

    df["atr_5"] = df.groupby("trading_symbol")["hl_range"].transform(lambda x: x.rolling(5).mean())

    # Volume and Volatility
    df["volume_spike_ratio"] = df["volume"] / df.groupby("trading_symbol")["volume"].transform(lambda x: x.rolling(3).mean())

    df["range_compression_ratio"] = df["hl_range"] / df.groupby("trading_symbol")["hl_range"].transform(lambda x: x.rolling(3).mean())

    rolling_mean = df.groupby("trading_symbol")["close"].transform(lambda x: x.rolling(20).mean())
    rolling_std = df.groupby("trading_symbol")["close"].transform(lambda x: x.rolling(20).std())
    upper_bb = rolling_mean + (2 * rolling_std)
    lower_bb = rolling_mean - (2 * rolling_std)
    bb_width = (upper_bb - lower_bb) / rolling_mean
    df["volatility_squeeze"] = bb_width / bb_width.rolling(20).mean()

    # Trend Zone Strength
    up_move = df.groupby("trading_symbol")["high"].diff()
    down_move = df.groupby("trading_symbol")["low"].diff().abs()
    dm = np.where(up_move > down_move, up_move, 0)
    df["trend_zone_strength"] = pd.Series(dm).rolling(14).mean()

    # Add FO Eligible
    symbol_map = symbol_df.set_index("trading_symbol")["fo_eligible"].to_dict()
    df["fo_eligible"] = df["trading_symbol"].map(symbol_map).fillna(False)

    # Select only columns we need for inserting into features_data
    features_cols = [
        "trading_symbol", "exchange", "date",
        "price_change_t_1", "gap_pct", "hl_range", "body_to_range_ratio",
        "lower_wick_pct", "upper_wick_pct", "closing_strength",
        "distance_from_ema_5", "return_3d", "return_5d",
        "position_in_range_5d", "atr_5",
        "volume_spike_ratio", "range_compression_ratio", "volatility_squeeze", "trend_zone_strength",
        "fo_eligible"
    ]

    return df[features_cols]
