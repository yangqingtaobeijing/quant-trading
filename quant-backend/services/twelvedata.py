"""
Twelve Data API wrapper for US equities.
Rate limit: 8 req/min on free plan → enforce ~8s sleep between requests.
Cache TTL: 15 minutes (CACHE_TTL_SECONDS).
"""
import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone

import httpx

logger = logging.getLogger(__name__)

API_KEY = os.getenv("TWELVE_DATA_API_KEY", "2baa491ec3804f86a76c0000f86be6ba")
BASE_URL = "https://api.twelvedata.com"
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "900"))

# Simple in-process cache to avoid hammering the API
_cache: dict[str, tuple[datetime, dict]] = {}
_request_lock = asyncio.Lock()
_last_request_time: datetime | None = None
MIN_INTERVAL_SECS = 8  # 8 req/min → ≥7.5 s between requests


async def _throttle():
    """Ensure at least MIN_INTERVAL_SECS between API calls."""
    global _last_request_time
    async with _request_lock:
        if _last_request_time is not None:
            elapsed = (datetime.now(timezone.utc) - _last_request_time).total_seconds()
            if elapsed < MIN_INTERVAL_SECS:
                await asyncio.sleep(MIN_INTERVAL_SECS - elapsed)
        _last_request_time = datetime.now(timezone.utc)


def _is_cache_valid(key: str) -> bool:
    if key not in _cache:
        return False
    cached_at, _ = _cache[key]
    return (datetime.now(timezone.utc) - cached_at).total_seconds() < CACHE_TTL


async def get_time_series(symbol: str, interval: str = "1day", outputsize: int = 120) -> list[dict]:
    """
    Returns a list of OHLCV dicts sorted ascending by datetime.
    Raises on API error.
    """
    cache_key = f"ts:{symbol}:{interval}:{outputsize}"
    if _is_cache_valid(cache_key):
        _, data = _cache[cache_key]
        return data

    await _throttle()
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": API_KEY,
        "order": "ASC",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{BASE_URL}/time_series", params=params)
        resp.raise_for_status()
        payload = resp.json()

    if payload.get("status") == "error":
        raise ValueError(f"Twelve Data error for {symbol}: {payload.get('message')}")

    values = payload.get("values", [])
    bars = []
    for v in values:
        bars.append({
            "datetime": v["datetime"],
            "open":   float(v["open"]),
            "high":   float(v["high"]),
            "low":    float(v["low"]),
            "close":  float(v["close"]),
            "volume": float(v.get("volume", 0) or 0),
        })

    _cache[cache_key] = (datetime.now(timezone.utc), bars)
    return bars


async def get_price(symbol: str) -> dict:
    """
    Returns {"symbol": ..., "price": float, "change_pct": float}.
    Falls back to last close from time_series if /price fails.
    """
    cache_key = f"price:{symbol}"
    if _is_cache_valid(cache_key):
        _, data = _cache[cache_key]
        return data

    await _throttle()
    params = {"symbol": symbol, "apikey": API_KEY}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{BASE_URL}/price", params=params)
        resp.raise_for_status()
        payload = resp.json()

    price = float(payload.get("price", 0) or 0)

    # Fetch previous close for change_pct via eod endpoint (best-effort)
    change_pct = None
    try:
        await _throttle()
        async with httpx.AsyncClient(timeout=30) as client:
            resp2 = await client.get(f"{BASE_URL}/eod", params=params)
            resp2.raise_for_status()
            eod = resp2.json()
            prev_close = float(eod.get("close", 0) or 0)
            if prev_close:
                change_pct = round((price - prev_close) / prev_close * 100, 4)
    except Exception:
        pass

    result = {"symbol": symbol, "price": price, "change_pct": change_pct}
    _cache[cache_key] = (datetime.now(timezone.utc), result)
    return result
