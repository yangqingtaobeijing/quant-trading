"""
Portfolio router — /api/portfolio
"""
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from database import get_db
from models import (
    PortfolioCreate,
    PortfolioResponse,
    PortfolioSummary,
    PortfolioUpdate,
)
from services import akshare_svc, twelvedata

logger = logging.getLogger(__name__)
router = APIRouter()


async def _get_current_price(symbol: str, market: str) -> Optional[float]:
    try:
        if market == "cn":
            data = await akshare_svc.get_price(symbol)
        else:
            data = await twelvedata.get_price(symbol)
        return data.get("price")
    except Exception as e:
        logger.warning(f"price fetch failed {symbol}: {e}")
        return None


def _row_to_response(row: dict, current_price: Optional[float] = None) -> PortfolioResponse:
    buy_price = float(row["buy_price"])
    quantity  = float(row["quantity"])
    cost      = buy_price * quantity

    pnl      = None
    pnl_pct  = None
    if current_price is not None:
        pnl     = round((current_price - buy_price) * quantity, 4)
        pnl_pct = round((current_price - buy_price) / buy_price * 100, 4) if buy_price else None

    return PortfolioResponse(
        id=row["id"],
        symbol=row["symbol"],
        market=row.get("market", "us"),
        buy_price=buy_price,
        quantity=quantity,
        buy_date=row["buy_date"],
        stop_loss=row.get("stop_loss"),
        take_profit=row.get("take_profit"),
        strategy=row.get("strategy"),
        note=row.get("note"),
        current_price=current_price,
        unrealized_pnl=pnl,
        unrealized_pnl_pct=pnl_pct,
    )


@router.get("/portfolio", response_model=List[PortfolioResponse])
async def list_portfolio(db=Depends(get_db)):
    async with db.execute("SELECT * FROM portfolio ORDER BY id") as cur:
        rows = await cur.fetchall()

    result = []
    for row in rows:
        r = dict(row)
        price = await _get_current_price(r["symbol"], r.get("market", "us"))
        result.append(_row_to_response(r, price))
    return result


@router.post("/portfolio", response_model=PortfolioResponse, status_code=201)
async def add_position(item: PortfolioCreate, db=Depends(get_db)):
    cur = await db.execute(
        """
        INSERT INTO portfolio (symbol, market, buy_price, quantity, buy_date,
                               stop_loss, take_profit, strategy, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item.symbol, item.market, item.buy_price, item.quantity, item.buy_date,
            item.stop_loss, item.take_profit, item.strategy, item.note,
        ),
    )
    await db.commit()
    row_id = cur.lastrowid
    async with db.execute("SELECT * FROM portfolio WHERE id=?", (row_id,)) as c:
        row = await c.fetchone()
    price = await _get_current_price(item.symbol, item.market)
    return _row_to_response(dict(row), price)


@router.put("/portfolio/{position_id}", response_model=PortfolioResponse)
async def update_position(position_id: int, update: PortfolioUpdate, db=Depends(get_db)):
    async with db.execute("SELECT * FROM portfolio WHERE id=?", (position_id,)) as cur:
        row = await cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Position not found")

    r = dict(row)
    stop_loss   = update.stop_loss   if update.stop_loss   is not None else r.get("stop_loss")
    take_profit = update.take_profit if update.take_profit is not None else r.get("take_profit")
    note        = update.note        if update.note        is not None else r.get("note")

    await db.execute(
        "UPDATE portfolio SET stop_loss=?, take_profit=?, note=? WHERE id=?",
        (stop_loss, take_profit, note, position_id),
    )
    await db.commit()

    async with db.execute("SELECT * FROM portfolio WHERE id=?", (position_id,)) as c:
        updated = await c.fetchone()
    price = await _get_current_price(r["symbol"], r.get("market", "us"))
    return _row_to_response(dict(updated), price)


@router.delete("/portfolio/{position_id}", status_code=204)
async def delete_position(position_id: int, db=Depends(get_db)):
    async with db.execute("SELECT id FROM portfolio WHERE id=?", (position_id,)) as cur:
        if not await cur.fetchone():
            raise HTTPException(status_code=404, detail="Position not found")
    await db.execute("DELETE FROM portfolio WHERE id=?", (position_id,))
    await db.commit()


@router.get("/portfolio/summary", response_model=PortfolioSummary)
async def portfolio_summary(db=Depends(get_db)):
    async with db.execute("SELECT * FROM portfolio ORDER BY id") as cur:
        rows = await cur.fetchall()

    total_cost  = 0.0
    total_value = 0.0

    for row in rows:
        r = dict(row)
        buy_price = float(r["buy_price"])
        quantity  = float(r["quantity"])
        total_cost += buy_price * quantity

        price = await _get_current_price(r["symbol"], r.get("market", "us"))
        cur_price = price if price is not None else buy_price
        total_value += cur_price * quantity

    total_pnl = total_value - total_cost
    pnl_pct   = round(total_pnl / total_cost * 100, 4) if total_cost else 0.0

    return PortfolioSummary(
        total_cost=round(total_cost, 4),
        total_value=round(total_value, 4),
        total_unrealized_pnl=round(total_pnl, 4),
        total_unrealized_pnl_pct=pnl_pct,
        position_count=len(rows),
        max_drawdown=None,  # Would require historical portfolio value tracking
    )
