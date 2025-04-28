# core/features/feature_engineer.py

import pandas as pd
import numpy as np

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_features(eod_df: pd.DataFrame, symbol_df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes raw EOD candle data and symbol master data, returns dataframe with 15 core features calculated.
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

    # --- New Features: (Cleanly integrated) ---

    df["rsi_14"] = df.groupby("trading_symbol")["close"].transform(lambda x: calculate_rsi(x))
    
    df["ema_50"] = df.groupby("trading_symbol")["close"].transform(lambda x: x.ewm(span=50, adjust=False).mean())
    df["close_ema50_gap_pct"] = (df["close"] - df["ema_50"]) / df["ema_50"] * 100

    df["prev_close"] = df.groupby("trading_symbol")["close"].shift(1)
    df["open_gap_pct"] = (df["open"] - df["prev_close"]) / df["prev_close"] * 100

    ema_12 = df.groupby("trading_symbol")["close"].transform(lambda x: x.ewm(span=12, adjust=False).mean())
    ema_26 = df.groupby("trading_symbol")["close"].transform(lambda x: x.ewm(span=26, adjust=False).mean())
    df["macd_line"] = ema_12 - ema_26
    df["macd_signal"] = df.groupby("trading_symbol")["macd_line"].transform(lambda x: x.ewm(span=9, adjust=False).mean())
    df["macd_histogram"] = df["macd_line"] - df["macd_signal"]

    df["tr1"] = df["high"] - df["low"]
    df["tr2"] = (df["high"] - df["close"].shift()).abs()
    df["tr3"] = (df["low"] - df["close"].shift()).abs()
    df["true_range"] = df[["tr1", "tr2", "tr3"]].max(axis=1)
    df["atr_14"] = df.groupby("trading_symbol")["true_range"].transform(lambda x: x.rolling(14).mean())
    df["atr_14_normalized"] = df["atr_14"] / df["close"]

    # Add FO Eligible (still needed)
    symbol_map = symbol_df.set_index("trading_symbol")["fo_eligible"].to_dict()
    df["fo_eligible"] = df["trading_symbol"].map(symbol_map).fillna(False)

    # Final feature selection
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
        "fo_eligible",
        # New Features
        "rsi_14",
        "close_ema50_gap_pct",
        "open_gap_pct",
        "macd_histogram",
        "atr_14_normalized"
    ]

    return df[features_cols]
