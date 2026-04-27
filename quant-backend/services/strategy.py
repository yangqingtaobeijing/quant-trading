"""
Strategy engine.

Strategy A – EMA Cross
  BUY  : EMA20 crosses above EMA60 (prev EMA20 < EMA60, cur EMA20 > EMA60)
  SELL : EMA20 crosses below EMA60

Strategy B – RSI Mean Reversion
  OVERSOLD  : RSI(14) < 30 for 2 consecutive bars
  OVERBOUGHT: RSI(14) > 70 for 2 consecutive bars
"""
import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Attempt to import pandas_ta; fall back gracefully
try:
    import pandas_ta as ta
    _HAS_PANDAS_TA = True
except ImportError:
    _HAS_PANDAS_TA = False
    logger.warning("pandas_ta not available — indicators will be None")


def _safe_float(val) -> Optional[float]:
    try:
        f = float(val)
        return None if pd.isna(f) else round(f, 6)
    except (TypeError, ValueError):
        return None


def compute_indicators(bars: list[dict]) -> pd.DataFrame:
    """
    Given a list of OHLCV dicts (ascending), return a DataFrame with
    all technical indicators appended.
    """
    if not bars or len(bars) < 2:
        return pd.DataFrame()

    df = pd.DataFrame(bars)
    df["close"] = df["close"].astype(float)
    df["high"]  = df["high"].astype(float)
    df["low"]   = df["low"].astype(float)
    df["open"]  = df["open"].astype(float)
    df["volume"] = df["volume"].astype(float)

    if not _HAS_PANDAS_TA:
        for col in ("ema20", "ema60", "rsi14", "macd", "signal_line", "atr14", "bb_upper", "bb_lower"):
            df[col] = None
        return df

    # EMA
    df["ema20"] = ta.ema(df["close"], length=20)
    df["ema60"] = ta.ema(df["close"], length=60)

    # RSI
    df["rsi14"] = ta.rsi(df["close"], length=14)

    # MACD (default 12, 26, 9)
    # Columns: MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
    macd_df = ta.macd(df["close"])
    if macd_df is not None and not macd_df.empty:
        cols = macd_df.columns.tolist()
        macd_col   = [c for c in cols if c.startswith("MACD_")]
        signal_col = [c for c in cols if c.startswith("MACDs")]
        df["macd"]        = macd_df[macd_col[0]]   if macd_col   else macd_df.iloc[:, 0]
        df["signal_line"] = macd_df[signal_col[0]] if signal_col else macd_df.iloc[:, 2]
    else:
        df["macd"] = None
        df["signal_line"] = None

    # ATR
    df["atr14"] = ta.atr(df["high"], df["low"], df["close"], length=14)

    # Bollinger Bands
    # Column names vary by pandas-ta version:
    #   older : BBL_20_2.0, BBU_20_2.0
    #   newer : BBL_20_2.0_2.0, BBU_20_2.0_2.0
    bb_df = ta.bbands(df["close"], length=20)
    if bb_df is not None and not bb_df.empty:
        cols = bb_df.columns.tolist()
        lower_col = [c for c in cols if c.upper().startswith("BBL")]
        upper_col = [c for c in cols if c.upper().startswith("BBU")]
        df["bb_lower"] = bb_df[lower_col[0]] if lower_col else None
        df["bb_upper"] = bb_df[upper_col[0]] if upper_col else None
    else:
        df["bb_lower"] = None
        df["bb_upper"] = None

    return df


def detect_signals(symbol: str, market: str, bars: list[dict]) -> list[dict]:
    """
    Run Strategy A & B on the provided bars.
    Returns a list of signal dicts (may be empty).
    """
    if len(bars) < 62:
        return []

    df = compute_indicators(bars)
    if df.empty:
        return []

    signals = []
    latest = df.iloc[-1]

    # ── Strategy A: EMA Cross ─────────────────────────────────────────────────
    if len(df) >= 2:
        prev = df.iloc[-2]
        cur  = df.iloc[-1]

        prev_e20 = _safe_float(prev.get("ema20"))
        prev_e60 = _safe_float(prev.get("ema60"))
        cur_e20  = _safe_float(cur.get("ema20"))
        cur_e60  = _safe_float(cur.get("ema60"))

        if all(v is not None for v in (prev_e20, prev_e60, cur_e20, cur_e60)):
            # Golden cross
            if prev_e20 < prev_e60 and cur_e20 > cur_e60:
                signals.append({
                    "symbol":      symbol,
                    "market":      market,
                    "signal_type": "BUY",
                    "price":       _safe_float(cur["close"]),
                    "strategy":    "EMA_CROSS",
                })
            # Death cross
            elif prev_e20 > prev_e60 and cur_e20 < cur_e60:
                signals.append({
                    "symbol":      symbol,
                    "market":      market,
                    "signal_type": "SELL",
                    "price":       _safe_float(cur["close"]),
                    "strategy":    "EMA_CROSS",
                })

    # ── Strategy B: RSI Mean Reversion ────────────────────────────────────────
    if len(df) >= 2:
        rsi_cur  = _safe_float(df.iloc[-1].get("rsi14"))
        rsi_prev = _safe_float(df.iloc[-2].get("rsi14"))

        if rsi_cur is not None and rsi_prev is not None:
            if rsi_cur < 30 and rsi_prev < 30:
                signals.append({
                    "symbol":      symbol,
                    "market":      market,
                    "signal_type": "OVERSOLD",
                    "price":       _safe_float(df.iloc[-1]["close"]),
                    "strategy":    "RSI_REVERSION",
                })
            elif rsi_cur > 70 and rsi_prev > 70:
                signals.append({
                    "symbol":      symbol,
                    "market":      market,
                    "signal_type": "OVERBOUGHT",
                    "price":       _safe_float(df.iloc[-1]["close"]),
                    "strategy":    "RSI_REVERSION",
                })

    return signals


def get_latest_indicators(bars: list[dict]) -> dict:
    """Return the most recent row of indicators as a flat dict."""
    if not bars:
        return {}
    df = compute_indicators(bars)
    if df.empty:
        return {}
    row = df.iloc[-1]
    return {
        "ema20":       _safe_float(row.get("ema20")),
        "ema60":       _safe_float(row.get("ema60")),
        "rsi14":       _safe_float(row.get("rsi14")),
        "macd":        _safe_float(row.get("macd")),
        "signal_line": _safe_float(row.get("signal_line")),
        "atr14":       _safe_float(row.get("atr14")),
        "bb_upper":    _safe_float(row.get("bb_upper")),
        "bb_lower":    _safe_float(row.get("bb_lower")),
    }


def get_kline_with_indicators(bars: list[dict]) -> list[dict]:
    """Return full bars list with indicators attached."""
    df = compute_indicators(bars)
    if df.empty:
        return []
    result = []
    for _, row in df.iterrows():
        result.append({
            "datetime":    str(row.get("datetime", "")),
            "open":        _safe_float(row.get("open")),
            "high":        _safe_float(row.get("high")),
            "low":         _safe_float(row.get("low")),
            "close":       _safe_float(row.get("close")),
            "volume":      _safe_float(row.get("volume")),
            "ema20":       _safe_float(row.get("ema20")),
            "ema60":       _safe_float(row.get("ema60")),
            "rsi14":       _safe_float(row.get("rsi14")),
            "macd":        _safe_float(row.get("macd")),
            "signal_line": _safe_float(row.get("signal_line")),
            "atr14":       _safe_float(row.get("atr14")),
            "bb_upper":    _safe_float(row.get("bb_upper")),
            "bb_lower":    _safe_float(row.get("bb_lower")),
        })
    return result
