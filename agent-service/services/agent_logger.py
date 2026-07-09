"""
Agent Logger
============
Structured, persistent logging for every agent event in the pipeline.

What it records per event
--------------------------
    job_id       – pipeline job identifier
    agent_name   – e.g. "Research Agent", "Idea Guard"
    event_type   – "start" | "complete" | "error" | "pipeline_complete"
    duration_s   – wall-clock seconds the agent ran
    scores       – dict of numeric scores extracted from the agent output
    output_keys  – list of top-level keys present in the result dict
    error_msg    – error message if event_type == "error"
    timestamp    – ISO-8601 UTC

Where it writes
---------------
    1. Rotating file  logs/agent-service.log  (5 MB × 5 backups)
       → always active, no configuration needed
    2. Supabase table agent_events
       → only when SUPABASE_URL + SUPABASE_SERVICE_KEY are set in .env

Contract
--------
- All public functions are fire-and-forget coroutines: they NEVER raise.
- They add zero latency to the pipeline (called via asyncio.create_task).
- The file logger is thread-safe (RotatingFileHandler + GIL).
- If Supabase is down or misconfigured, only file logging happens.

Usage (in pipeline.py)
----------------------
    import asyncio
    from services.agent_logger import log_agent_start, log_agent_complete, log_agent_error

    asyncio.create_task(log_agent_start(job_id, agent_name))
    asyncio.create_task(log_agent_complete(job_id, agent_name, duration_s, result))
    asyncio.create_task(log_agent_error(job_id, agent_name, duration_s, error_msg))
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List, Optional

from config import settings

# ─── File logger (module-level singleton) ────────────────────────────────────

_LOGS_DIR  = os.path.join(os.path.dirname(__file__), "..", "logs")
_LOG_FILE  = os.path.join(_LOGS_DIR, "agent-events.log")
_MAX_BYTES = 5 * 1024 * 1024   # 5 MB
_BACKUPS   = 5


def _get_file_logger() -> logging.Logger:
    """Return (and lazily initialise) the rotating-file agent event logger."""
    name = "agent-service.events"
    lg   = logging.getLogger(name)
    if lg.handlers:        # already set up
        return lg
    try:
        os.makedirs(_LOGS_DIR, exist_ok=True)
        handler = RotatingFileHandler(
            _LOG_FILE,
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUPS,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))   # raw JSON lines
        lg.addHandler(handler)
        lg.setLevel(logging.INFO)
        lg.propagate = False   # don't duplicate to console
    except Exception as exc:
        # If we cannot open the file (e.g. read-only FS), fall back silently
        logging.getLogger("agent-service").warning(
            "agent_logger: could not open log file %s: %s", _LOG_FILE, exc
        )
    return lg


_file_logger = _get_file_logger()


# ─── Score extraction ─────────────────────────────────────────────────────────

# Maps agent pipeline key → (result_field, score_field)
_SCORE_MAP: Dict[str, tuple[str, str]] = {
    "idea_guard":        ("idea_guard",        "clarity_score"),
    "research_gap":      ("research_gaps",     "novelty_score"),
    "research_gaps":     ("research_gaps",     "novelty_score"),
    "competitors":       ("competitors",       "market_saturation_score"),
    "competitor":        ("competitors",       "market_saturation_score"),
    "scientific":        ("scientific",        "research_maturity_score"),
    "patent":            ("patents",           "patent_density_score"),
    "patents":           ("patents",           "patent_density_score"),
    "funding":           ("funding",           "funding_activity_score"),
    "opportunity":       ("opportunities",     "opportunity_score"),
    "opportunities":     ("opportunities",     "opportunity_score"),
    "risk":              ("risks",             "risk_score"),
    "risks":             ("risks",             "risk_score"),
    "innovation_score":  ("innovation_score",  "innovation_score"),
    "innovation_scoring":("innovation_score",  "innovation_score"),
    "report":            ("report",            "market_score"),
}


def _extract_scores(agent_name: str, result: Dict[str, Any]) -> Dict[str, float]:
    """
    Extract relevant numeric scores from an agent result dict.
    Returns a dict that may be empty if the agent produces no scores.
    """
    scores: Dict[str, float] = {}
    if not isinstance(result, dict):
        return scores

    # Always try to grab every known score field directly from the result
    for field in (
        "innovation_score", "opportunity_score", "market_score",
        "market_saturation_score", "research_maturity_score",
        "patent_density_score", "funding_activity_score",
        "novelty_score", "risk_score", "clarity_score", "vagueness_score",
    ):
        val = result.get(field)
        if val is not None:
            try:
                scores[field] = float(val)
            except (TypeError, ValueError):
                pass

    return scores


# ─── Supabase persistence (fire-and-forget) ───────────────────────────────────

def _supabase_configured() -> bool:
    return bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY)


async def _persist_to_supabase(record: Dict[str, Any]) -> None:
    """Insert one agent event record into Supabase. Silently ignores all errors."""
    if not _supabase_configured():
        return
    try:
        from supabase import acreate_client
        client = await acreate_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SERVICE_KEY,
        )
        await client.table("agent_events").insert(record).execute()
    except Exception as exc:
        logging.getLogger("agent-service").debug(
            "agent_logger: Supabase insert failed: %s", exc
        )


# ─── Internal write ───────────────────────────────────────────────────────────

def _write_file(record: Dict[str, Any]) -> None:
    """Append a JSON line to the rotating log file. Never raises."""
    try:
        _file_logger.info(json.dumps(record, default=str))
    except Exception:
        pass


def _build_record(
    job_id: str,
    agent_name: str,
    event_type: str,
    duration_s: Optional[float] = None,
    scores: Optional[Dict[str, float]] = None,
    output_keys: Optional[List[str]] = None,
    error_msg: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "timestamp":   datetime.now(timezone.utc).isoformat(),
        "job_id":      job_id,
        "agent_name":  agent_name,
        "event_type":  event_type,
        "duration_s":  round(duration_s, 3) if duration_s is not None else None,
        "scores":      scores or {},
        "output_keys": output_keys or [],
        "error_msg":   error_msg,
    }


# ─── Public API ───────────────────────────────────────────────────────────────

async def log_agent_start(job_id: str, agent_name: str) -> None:
    """Record that an agent has started. Fire-and-forget — never raises."""
    try:
        record = _build_record(job_id, agent_name, "start")
        _write_file(record)
        # No Supabase insert for start events — too chatty; only complete/error matter.
    except Exception:
        pass


async def log_agent_complete(
    job_id: str,
    agent_name: str,
    duration_s: float,
    result: Dict[str, Any],
) -> None:
    """
    Record a successful agent completion.

    Parameters
    ----------
    job_id      : str
    agent_name  : str
    duration_s  : float  Wall-clock seconds
    result      : dict   The dict returned by the agent (used to extract scores)
    """
    try:
        scores      = _extract_scores(agent_name, result)
        output_keys = list(result.keys()) if isinstance(result, dict) else []
        record      = _build_record(
            job_id, agent_name, "complete",
            duration_s=duration_s,
            scores=scores,
            output_keys=output_keys,
        )
        _write_file(record)
        asyncio.create_task(_persist_to_supabase({
            "job_id":      job_id,
            "agent_name":  agent_name,
            "event_type":  "complete",
            "duration_s":  record["duration_s"],
            "scores":      scores,
            "output_keys": output_keys,
            "error_msg":   None,
            "timestamp":   record["timestamp"],
        }))
    except Exception:
        pass


async def log_agent_error(
    job_id: str,
    agent_name: str,
    duration_s: float,
    error_msg: str,
) -> None:
    """Record a failed agent run. Fire-and-forget — never raises."""
    try:
        record = _build_record(
            job_id, agent_name, "error",
            duration_s=duration_s,
            error_msg=str(error_msg)[:500],
        )
        _write_file(record)
        asyncio.create_task(_persist_to_supabase(record))
    except Exception:
        pass


async def log_pipeline_complete(
    job_id: str,
    total_duration_s: float,
    final_state: Dict[str, Any],
) -> None:
    """
    Record pipeline-level completion with all final scores.
    Called once per job after all agents finish.
    """
    try:
        # Collect all numeric scores from the final state
        all_scores: Dict[str, float] = {}
        score_fields = {
            "innovation_score":       ("innovation_score",  "innovation_score"),
            "market_score":           ("report",            "market_score"),
            "opportunity_score":      ("opportunities",     "opportunity_score"),
            "market_saturation_score":("competitors",       "market_saturation_score"),
            "research_maturity_score":("scientific",        "research_maturity_score"),
            "patent_density_score":   ("patents",           "patent_density_score"),
            "funding_activity_score": ("funding",           "funding_activity_score"),
            "novelty_score":          ("research_gaps",     "novelty_score"),
            "risk_score":             ("risks",             "risk_score"),
        }
        for score_name, (state_key, field) in score_fields.items():
            section = final_state.get(state_key) or {}
            if isinstance(section, dict):
                val = section.get(field)
                if val is not None:
                    try:
                        all_scores[score_name] = float(val)
                    except (TypeError, ValueError):
                        pass

        record = _build_record(
            job_id, "PIPELINE", "pipeline_complete",
            duration_s=total_duration_s,
            scores=all_scores,
        )
        _write_file(record)
        asyncio.create_task(_persist_to_supabase({
            **record,
            "agent_name": "PIPELINE",
        }))
    except Exception:
        pass
