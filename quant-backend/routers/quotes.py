"""
Quotes router — /api/quotes and /api/watchlist and /api/kline
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from database import get_db
from models import (
    BatchQuoteRequest,
    KlineBar,
    QuoteResponse,
    WatchlistItem,
    WatchlistResponse,
)
from services import akshare_svc, twelvedata
from services.strategy import get_kline_with_indicators, get_latest_indicators

logger = logging.getLogger(__name__)
router = APIRouter()


# ─── Helpers ──────────────────────────────────────────────────────────────────

async def _fetch_bars(symbol: str, market: str, limit: int = 120) -> list[dict]:
    if market == "cn":
        return await akshare_svc.get_time_series(symbol, outputsize=limit)
    else:
        return await twelvedata.get_time_series(symbol, outputsize=limit)


async def _fetch_price(symbol: str, market: str) -> dict:
    if market == "cn":
        return await akshare_svc.get_price(symbol)
    else:
        return await twelvedata.get_price(symbol)


async def _build_quote(symbol: str, market: str) -> QuoteResponse:
    bars = await _fetch_bars(symbol, market)
    price_data = await _fetch_price(symbol, market)
    indicators = get_latest_indicators(bars)

    # volume from last bar
    volume = None
    if bars:
        volume = bars[-1].get("volume")

    return QuoteResponse(
        symbol=symbol,
        market=market,
        price=price_data.get("price"),
        change_pct=price_data.get("change_pct"),
        volume=volume,
        **indicators,
    )


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.get("/quotes/{symbol}", response_model=QuoteResponse)
async def get_quote(symbol: str, market: str = Query("us", regex="^(us|cn)$")):
    try:
        return await _build_quote(symbol.upper() if market == "us" else symbol, market)
    except Exception as e:
        logger.error(f"get_quote error {symbol}: {e}")
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/quotes/batch")
async def batch_quotes(body: BatchQuoteRequest):
    results = []
    for item in body.symbols:
        try:
            q = await _build_quote(
                item.symbol.upper() if item.market == "us" else item.symbol,
                item.market,
            )
            results.append(q.model_dump())
        except Exception as e:
            logger.warning(f"batch_quotes skip {item.symbol}: {e}")
            results.append({"symbol": item.symbol, "market": item.market, "error": str(e)})
    return results


@router.get("/watchlist", response_model=List[WatchlistResponse])
async def get_watchlist(db=Depends(get_db)):
    async with db.execute("SELECT symbol, market, name, added_at FROM watchlist ORDER BY added_at") as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


@router.post("/watchlist", response_model=WatchlistResponse, status_code=201)
async def add_watchlist(item: WatchlistItem, db=Depends(get_db)):
    from datetime import datetime
    now = datetime.utcnow().isoformat()
    try:
        await db.execute(
            "INSERT OR IGNORE INTO watchlist (symbol, market, name, added_at) VALUES (?, ?, ?, ?)",
            (item.symbol, item.market, item.name, now),
        )
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"symbol": item.symbol, "market": item.market, "name": item.name, "added_at": now}


@router.delete("/watchlist/{symbol}", status_code=204)
async def delete_watchlist(symbol: str, market: str = Query("us"), db=Depends(get_db)):
    await db.execute("DELETE FROM watchlist WHERE symbol=? AND market=?", (symbol, market))
    await db.commit()


@router.get("/kline/{symbol}")
async def get_kline(
    symbol: str,
    market: str = Query("us", regex="^(us|cn)$"),
    period: str = Query("daily"),
    limit: int = Query(120, ge=10, le=500),
):
    try:
        bars = await _fetch_bars(
            symbol.upper() if market == "us" else symbol,
            market,
            limit=limit,
        )
        kline = get_kline_with_indicators(bars)
        return kline
    except Exception as e:
        logger.error(f"get_kline error {symbol}: {e}")
        raise HTTPException(status_code=502, detail=str(e))
