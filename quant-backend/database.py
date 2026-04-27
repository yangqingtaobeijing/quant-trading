"""
SQLite database initialization and connection management.
"""
import aiosqlite
import os
from datetime import datetime

DB_PATH = os.getenv("DATABASE_URL", "./quant.db")

CREATE_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS watchlist (
        symbol      TEXT NOT NULL,
        market      TEXT NOT NULL DEFAULT 'us',
        name        TEXT,
        added_at    TEXT NOT NULL,
        PRIMARY KEY (symbol, market)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS signals (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol      TEXT NOT NULL,
        market      TEXT NOT NULL DEFAULT 'us',
        signal_type TEXT NOT NULL,
        price       REAL,
        strategy    TEXT,
        created_at  TEXT NOT NULL,
        is_triggered INTEGER NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS portfolio (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol       TEXT NOT NULL,
        market       TEXT NOT NULL DEFAULT 'us',
        buy_price    REAL NOT NULL,
        quantity     REAL NOT NULL,
        buy_date     TEXT NOT NULL,
        stop_loss    REAL,
        take_profit  REAL,
        strategy     TEXT,
        note         TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS price_cache (
        symbol      TEXT NOT NULL,
        market      TEXT NOT NULL DEFAULT 'us',
        data_json   TEXT NOT NULL,
        updated_at  TEXT NOT NULL,
        PRIMARY KEY (symbol, market)
    )
    """,
]

INITIAL_WATCHLIST = [
    ("AAPL",   "us",  "Apple Inc."),
    ("MSFT",   "us",  "Microsoft Corp."),
    ("NVDA",   "us",  "NVIDIA Corp."),
    ("SPY",    "us",  "SPDR S&P 500 ETF"),
    ("QQQ",    "us",  "Invesco QQQ Trust"),
    ("600036", "cn",  "招商银行"),
    ("000001", "cn",  "平安银行"),
    ("600519", "cn",  "贵州茅台"),
]


async def get_db():
    """Async context manager for DB connection."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def init_db():
    """Create tables and seed initial watchlist."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        for sql in CREATE_TABLES_SQL:
            await db.execute(sql)
        await db.commit()

        now = datetime.utcnow().isoformat()
        for symbol, market, name in INITIAL_WATCHLIST:
            await db.execute(
                """
                INSERT OR IGNORE INTO watchlist (symbol, market, name, added_at)
                VALUES (?, ?, ?, ?)
                """,
                (symbol, market, name, now),
            )
        await db.commit()
