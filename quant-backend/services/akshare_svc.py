"""
AKShare service for A-share (China) market data.
All heavy AKShare calls are run in a thread pool executor to avoid blocking
the async event loop.
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from functools import lru_cache

logger = logging.getLogger(__name__)

# In-process cache: {key: (cached_at, data)}
_cache: dict[str, tuple[datetime, object]] = {}
CACHE_TTL = 900  # 15 minutes


def _is_cache_valid(key: str) -> bool:
    if key not in _cache:
        return False
    cached_at, _ = _cache[key]
    return (datetime.now(timezone.utc) - cached_at).total_seconds() < CACHE_TTL


def _fetch_hist_sync(symbol: str, start_date: str) -> list[dict]:
    """Synchronous AKShare call — runs in executor."""
    import akshare as ak
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date=start_date,
        adjust="qfq",
    )
    if df is None or df.empty:
        return []
    # Normalize column names
    df = df.rename(columns={
        "日期": "datetime",
        "开盘": "open",
        "最高": "high",
        "最低": "low",
        "收盘": "close",
        "成交量": "volume",
        "成交额": "amount",
        "涨跌幅": "change_pct",
    })
    # Sort ascending
    df = df.sort_values("datetime")
    records = []
    for _, row in df.iterrows():
        records.append({
            "datetime":   str(row["datetime"]),
            "open":       float(row.get("open", 0)),
            "high":       float(row.get("high", 0)),
            "low":        float(row.get("low", 0)),
            "close":      float(row.get("close", 0)),
            "volume":     float(row.get("volume", 0)),
        })
    return records


def _fetch_spot_sync(symbol: str) -> dict | None:
    """Synchronous AKShare spot call — runs in executor."""
    import akshare as ak
    df = ak.stock_zh_a_spot_em()
    if df is None or df.empty:
        return None
    row = df[df["代码"] == symbol]
    if row.empty:
        return None
    r = row.iloc[0]
    price = float(r.get("最新价", 0) or 0)
    change_pct = float(r.get("涨跌幅", 0) or 0)
    volume = float(r.get("成交量", 0) or 0)
    name = str(r.get("名称", ""))
    return {
        "symbol": symbol,
        "name": name,
        "price": price,
        "change_pct": change_pct,
        "volume": volume,
    }


async def get_time_series(symbol: str, outputsize: int = 120) -> list[dict]:
    """Return ascending OHLCV bars for a CN symbol."""
    cache_key = f"ts_cn:{symbol}:{outputsize}"
    if _is_cache_valid(cache_key):
        _, data = _cache[cache_key]
        return data

    start_date = (datetime.now() - timedelta(days=max(outputsize * 2, 365))).strftime("%Y%m%d")
    loop = asyncio.get_event_loop()
    try:
        bars = await loop.run_in_executor(None, _fetch_hist_sync, symbol, start_date)
    except Exception as e:
        logger.error(f"AKShare hist error for {symbol}: {e}")
        return []

    # Trim to last `outputsize` bars
    bars = bars[-outputsize:]
    _cache[cache_key] = (datetime.now(timezone.utc), bars)
    return bars


async def get_price(symbol: str) -> dict:
    """Return spot price for a CN symbol."""
    cache_key = f"price_cn:{symbol}"
    if _is_cache_valid(cache_key):
        _, data = _cache[cache_key]
        return data

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, _fetch_spot_sync, symbol)
    except Exception as e:
        logger.error(f"AKShare spot error for {symbol}: {e}")
        result = None

    if result is None:
        result = {"symbol": symbol, "price": None, "change_pct": None, "volume": None}

    _cache[cache_key] = (datetime.now(timezone.utc), result)
    return result
