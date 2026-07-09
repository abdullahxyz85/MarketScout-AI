from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from router import router

_LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")


def _setup_logging() -> None:
    """Configure console + rotating-file logging for the entire service."""
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt)

    # Rotating file: logs/agent-service.log  (5 MB × 5 backups)
    try:
        os.makedirs(_LOGS_DIR, exist_ok=True)
        fh = RotatingFileHandler(
            os.path.join(_LOGS_DIR, "agent-service.log"),
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        fh.setFormatter(logging.Formatter(fmt))
        logging.getLogger().addHandler(fh)
    except Exception as exc:
        logging.getLogger("agent-service").warning(
            "Could not set up log file: %s", exc
        )


_setup_logging()
logger = logging.getLogger("agent-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up: pre-compile the LangGraph pipeline at startup
    from orchestrator.pipeline import get_pipeline
    get_pipeline()
    logger.info("Agent service started — pipeline compiled and ready")
    yield
    logger.info("Agent service shutting down")


app = FastAPI(
    title="MarketScout AI — Agent Service",
    version="1.0.0",
    description=(
        "Autonomous multi-agent market intelligence service. "
        "Powered by AMD Instinct GPUs via Fireworks AI. "
        "Orchestrated with LangGraph."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "service": "agent-service",
        "llm_provider": "Fireworks AI (AMD Instinct GPUs)",
        "orchestration": "LangGraph",
    }
