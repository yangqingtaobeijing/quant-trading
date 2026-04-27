"""
APScheduler — runs signal scan every weekday after market close.
US: 16:30 ET ≈ 21:30 UTC (summer) / 22:30 UTC (winter) → use 22:00 UTC
CN: 15:30 CST = 07:30 UTC

The scheduler is started from main.py on app startup.
"""
import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="UTC")


async def _run_scan():
    """Perform a full signal scan across all watchlist symbols."""
    logger.info("Scheduler: starting signal scan")
    try:
        import aiosqlite
        from database import DB_PATH
        from services import akshare_svc, twelvedata
        from services.strategy import detect_signals
        from datetime import datetime

        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT symbol, market FROM watchlist") as cur:
                watchlist = await cur.fetchall()

            now = datetime.utcnow().isoformat()
            count = 0
            for row in watchlist:
                symbol = row["symbol"]
                market = row["market"]
                try:
                    if market == "cn":
                        bars = await akshare_svc.get_time_series(symbol, outputsize=120)
                    else:
                        bars = await twelvedata.get_time_series(symbol, outputsize=120)

                    sigs = detect_signals(symbol, market, bars)
                    for s in sigs:
                        await db.execute(
                            """
                            INSERT INTO signals (symbol, market, signal_type, price, strategy, created_at, is_triggered)
                            VALUES (?, ?, ?, ?, ?, ?, 0)
                            """,
                            (s["symbol"], s["market"], s["signal_type"], s.get("price"), s.get("strategy"), now),
                        )
                        count += 1
                except Exception as e:
                    logger.warning(f"Scheduler scan error for {symbol}: {e}")

            await db.commit()
            logger.info(f"Scheduler: scan complete — {count} new signals for {len(watchlist)} symbols")
    except Exception as e:
        logger.error(f"Scheduler: scan failed: {e}")


def start_scheduler():
    """Register jobs and start the scheduler."""
    # US close scan — 22:00 UTC Mon–Fri
    scheduler.add_job(
        _run_scan,
        CronTrigger(day_of_week="mon-fri", hour=22, minute=0, timezone="UTC"),
        id="us_close_scan",
        replace_existing=True,
        misfire_grace_time=600,
    )
    # CN close scan — 07:30 UTC Mon–Fri
    scheduler.add_job(
        _run_scan,
        CronTrigger(day_of_week="mon-fri", hour=7, minute=30, timezone="UTC"),
        id="cn_close_scan",
        replace_existing=True,
        misfire_grace_time=600,
    )
    scheduler.start()
    logger.info("Scheduler started (US close: 22:00 UTC, CN close: 07:30 UTC)")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
