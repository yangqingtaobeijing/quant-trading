"""
Pydantic models for request / response validation.
"""
from typing import List, Optional
from pydantic import BaseModel


# ─── Watchlist ────────────────────────────────────────────────────────────────

class WatchlistItem(BaseModel):
    symbol: str
    market: str = "us"
    name: Optional[str] = None


class WatchlistResponse(BaseModel):
    symbol: str
    market: str
    name: Optional[str]
    added_at: str


# ─── Quote / Kline ────────────────────────────────────────────────────────────

class QuoteResponse(BaseModel):
    symbol: str
    market: str
    price: Optional[float]
    change_pct: Optional[float]
    volume: Optional[float]
    ema20: Optional[float]
    ema60: Optional[float]
    rsi14: Optional[float]
    macd: Optional[float]
    signal_line: Optional[float]
    atr14: Optional[float]
    bb_upper: Optional[float]
    bb_lower: Optional[float]
    cached: bool = False


class BatchQuoteRequest(BaseModel):
    symbols: List[WatchlistItem]


class KlineBar(BaseModel):
    datetime: str
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float]
    ema20: Optional[float]
    ema60: Optional[float]
    rsi14: Optional[float]
    macd: Optional[float]
    signal_line: Optional[float]
    atr14: Optional[float]
    bb_upper: Optional[float]
    bb_lower: Optional[float]


# ─── Signals ──────────────────────────────────────────────────────────────────

class SignalResponse(BaseModel):
    id: int
    symbol: str
    market: str
    signal_type: str
    price: Optional[float]
    strategy: Optional[str]
    created_at: str
    is_triggered: bool


class ScanResponse(BaseModel):
    scanned: int
    new_signals: int
    signals: List[SignalResponse]


# ─── Portfolio ────────────────────────────────────────────────────────────────

class PortfolioCreate(BaseModel):
    symbol: str
    market: str = "us"
    buy_price: float
    quantity: float
    buy_date: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    strategy: Optional[str] = None
    note: Optional[str] = None


class PortfolioUpdate(BaseModel):
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    note: Optional[str] = None


class PortfolioResponse(BaseModel):
    id: int
    symbol: str
    market: str
    buy_price: float
    quantity: float
    buy_date: str
    stop_loss: Optional[float]
    take_profit: Optional[float]
    strategy: Optional[str]
    note: Optional[str]
    current_price: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    unrealized_pnl_pct: Optional[float] = None


class PortfolioSummary(BaseModel):
    total_cost: float
    total_value: float
    total_unrealized_pnl: float
    total_unrealized_pnl_pct: float
    position_count: int
    max_drawdown: Optional[float] = None
