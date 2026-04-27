"""
Signals router — /api/signals
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from database import get_db
from models import ScanResponse, SignalResponse
from services import akshare_svc, twelvedata
from services.strategy import detect_signals

logger = logging.getLogger(__name__)
router = APIRouter()


async def _fetch_bars(symbol: str, market: str) -> list[dict]:
    if market == "cn":
        return await akshare_svc.get_time_series(symbol, outputsize=120)
    else:
        return await twelvedata.get_time_series(symbol, outputsize=120)


def _row_to_signal(row) -> SignalResponse:
    r = dict(row)
    return SignalResponse(
        id=r["id"],
        symbol=r["symbol"],
        market=r.get("market", "us"),
        signal_type=r["signal_type"],
        price=r.get("price"),
        strategy=r.get("strategy"),
        created_at=r["created_at"],
        is_triggered=bool(r["is_triggered"]),
    )


@router.get("/signals", response_model=List[SignalResponse])
async def list_signals(
    symbol: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db=Depends(get_db),
):
    if symbol:
        async with db.execute(
            "SELECT * FROM signals WHERE symbol=? ORDER BY created_at DESC LIMIT ?",
            (symbol, limit),
        ) as cur:
            rows = await cur.fetchall()
    else:
        async with db.execute(
            "SELECT * FROM signals ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ) as cur:
            rows = await cur.fetchall()
    return [_row_to_signal(r) for r in rows]


@router.get("/signals/latest", response_model=List[SignalResponse])
async def latest_signals(db=Depends(get_db)):
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    async with db.execute(
        "SELECT * FROM signals WHERE created_at >= ? ORDER BY created_at DESC",
        (cutoff,),
    ) as cur:
        rows = await cur.fetchall()
    return [_row_to_signal(r) for r in rows]


@router.post("/signals/scan", response_model=ScanResponse)
async def scan_signals(db=Depends(get_db)):
    async with db.execute("SELECT symbol, market FROM watchlist") as cur:
        watchlist = await cur.fetchall()

    now = datetime.utcnow().isoformat()
    new_signals = []

    for row in watchlist:
        symbol = row["symbol"]
        market = row["market"]
        try:
            bars = await _fetch_bars(symbol, market)
            sigs = detect_signals(symbol, market, bars)
            for s in sigs:
                await db.execute(
                    """
                    INSERT INTO signals (symbol, market, signal_type, price, strategy, created_at, is_triggered)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                    """,
                    (s["symbol"], s["market"], s["signal_type"], s.get("price"), s.get("strategy"), now),
                )
                new_signals.append(s)
        except Exception as e:
            logger.warning(f"scan_signals error for {symbol}: {e}")

    await db.commit()

    # Fetch the newly inserted rows
    inserted: List[SignalResponse] = []
    if new_signals:
        async with db.execute(
            "SELECT * FROM signals WHERE created_at=? ORDER BY id DESC",
            (now,),
        ) as cur:
            rows = await cur.fetchall()
        inserted = [_row_to_signal(r) for r in rows]

    return ScanResponse(
        scanned=len(watchlist),
        new_signals=len(inserted),
        signals=inserted,
    )
