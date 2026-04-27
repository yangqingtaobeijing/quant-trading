"""
Quant Trading Backend — FastAPI entry point.
Port: 8888
"""
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from database import init_db
from routers import portfolio, quotes, signals
from scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initialising database …")
    await init_db()
    logger.info("Database ready.")
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()
    logger.info("Quant backend shutdown complete.")


app = FastAPI(
    title="Quant Trading Backend",
    version="1.0.0",
    description="Quantitative trading assistant — quotes, signals, portfolio management",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers under /api prefix
app.include_router(quotes.router,    prefix="/api", tags=["quotes"])
app.include_router(signals.router,   prefix="/api", tags=["signals"])
app.include_router(portfolio.router, prefix="/api", tags=["portfolio"])


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "service": "quant-backend", "port": 8888}


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
