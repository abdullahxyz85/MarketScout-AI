"""
Tests for services/agent_logger.py

Contract under test:
  - All public functions are fire-and-forget: they never raise
  - JSON lines are written to the rotating log file
  - Records have all required fields
  - Scores are correctly extracted from agent result dicts
  - Works correctly when Supabase is not configured
  - Works correctly with None / garbage inputs
"""
from __future__ import annotations

import asyncio
import json
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import services.agent_logger as agent_logger_module
from services.agent_logger import (
    _build_record,
    _extract_scores,
    log_agent_complete,
    log_agent_error,
    log_agent_start,
    log_pipeline_complete,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

def _research_result() -> dict:
    return {
        "market_overview": "Large market.",
        "key_players": ["A", "B"],
        "market_size_estimate": "$20B",
        "innovation_score": 72,
        "opportunity_score": 68,
        "sources": ["https://example.com"],
    }


def _pipeline_state() -> dict:
    return {
        "job_id":  "test-job",
        "idea":    "AI invoicing for SMBs",
        "industry": "FinTech",
        "innovation_score": {"innovation_score": 72, "grade": "B"},
        "report":           {"market_score": 78, "opportunity_score": 70},
        "opportunities":    {"opportunity_score": 70},
        "competitors":      {"market_saturation_score": 55},
        "scientific":       {"research_maturity_score": 68},
        "patents":          {"patent_density_score": 35},
        "funding":          {"funding_activity_score": 65},
        "research_gaps":    {"novelty_score": 74},
        "risks":            {"risk_score": 38},
    }


# ─── _build_record ────────────────────────────────────────────────────────────

def test_build_record_has_required_keys():
    r = _build_record("job-1", "Research Agent", "complete", duration_s=2.5)
    for key in ("timestamp", "job_id", "agent_name", "event_type", "duration_s", "scores", "output_keys", "error_msg"):
        assert key in r


def test_build_record_duration_rounded():
    r = _build_record("job-1", "Agent", "complete", duration_s=2.123456)
    assert r["duration_s"] == 2.123


def test_build_record_none_duration():
    r = _build_record("job-1", "Agent", "start")
    assert r["duration_s"] is None


def test_build_record_error_msg_set():
    r = _build_record("job-1", "Agent", "error", error_msg="kaboom")
    assert r["error_msg"] == "kaboom"


def test_build_record_scores_defaults_to_empty():
    r = _build_record("job-1", "Agent", "complete")
    assert r["scores"] == {}


# ─── _extract_scores ──────────────────────────────────────────────────────────

def test_extract_scores_from_innovation_result():
    result = {"innovation_score": 72, "grade": "B", "score_explanation": "ok"}
    scores = _extract_scores("innovation_scoring", result)
    assert scores.get("innovation_score") == 72.0


def test_extract_scores_from_opportunity_result():
    result = {"opportunity_score": 68, "market_gaps": ["gap1"]}
    scores = _extract_scores("opportunity", result)
    assert scores.get("opportunity_score") == 68.0


def test_extract_scores_from_competitor_result():
    result = {"market_saturation_score": 55, "competitors": []}
    scores = _extract_scores("competitor", result)
    assert scores.get("market_saturation_score") == 55.0


def test_extract_scores_ignores_non_numeric():
    result = {"innovation_score": "high", "grade": "B"}
    scores = _extract_scores("innovation_scoring", result)
    assert "innovation_score" not in scores


def test_extract_scores_empty_result():
    assert _extract_scores("research", {}) == {}


def test_extract_scores_none_result():
    assert _extract_scores("research", None) == {}


def test_extract_scores_multiple_fields():
    result = {
        "innovation_score": 72,
        "opportunity_score": 65,
        "risk_score": 38,
    }
    scores = _extract_scores("report", result)
    assert scores.get("innovation_score") == 72.0
    assert scores.get("opportunity_score") == 65.0
    assert scores.get("risk_score") == 38.0


# ─── File writing ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_log_agent_complete_writes_json_line(tmp_path):
    """Verify a valid JSON line is written to the log file."""
    log_file = tmp_path / "test-events.log"

    with patch.object(agent_logger_module, "_file_logger") as mock_logger:
        written_lines = []
        mock_logger.info = lambda msg: written_lines.append(msg)

        await log_agent_complete("job-1", "Research Agent", 2.5, _research_result())

    assert len(written_lines) == 1
    record = json.loads(written_lines[0])
    assert record["job_id"] == "job-1"
    assert record["agent_name"] == "Research Agent"
    assert record["event_type"] == "complete"
    assert record["duration_s"] == 2.5


@pytest.mark.asyncio
async def test_log_agent_error_writes_json_line():
    with patch.object(agent_logger_module, "_file_logger") as mock_logger:
        written_lines = []
        mock_logger.info = lambda msg: written_lines.append(msg)

        await log_agent_error("job-2", "SWOT Agent", 0.5, "Connection timeout")

    assert len(written_lines) == 1
    record = json.loads(written_lines[0])
    assert record["event_type"] == "error"
    assert record["error_msg"] == "Connection timeout"


@pytest.mark.asyncio
async def test_log_agent_start_writes_json_line():
    with patch.object(agent_logger_module, "_file_logger") as mock_logger:
        written_lines = []
        mock_logger.info = lambda msg: written_lines.append(msg)

        await log_agent_start("job-3", "Competitor Agent")

    assert len(written_lines) == 1
    record = json.loads(written_lines[0])
    assert record["event_type"] == "start"
    assert record["agent_name"] == "Competitor Agent"


@pytest.mark.asyncio
async def test_log_pipeline_complete_writes_json_line():
    with patch.object(agent_logger_module, "_file_logger") as mock_logger:
        written_lines = []
        mock_logger.info = lambda msg: written_lines.append(msg)

        await log_pipeline_complete("job-4", 45.3, _pipeline_state())

    assert len(written_lines) == 1
    record = json.loads(written_lines[0])
    assert record["event_type"] == "pipeline_complete"
    assert record["agent_name"] == "PIPELINE"
    assert record["scores"].get("innovation_score") == 72.0


# ─── Scores in pipeline_complete ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pipeline_complete_captures_all_scores():
    with patch.object(agent_logger_module, "_file_logger") as mock_logger:
        written_lines = []
        mock_logger.info = lambda msg: written_lines.append(msg)

        await log_pipeline_complete("job-5", 40.0, _pipeline_state())

    record = json.loads(written_lines[0])
    scores = record["scores"]
    assert scores.get("innovation_score")        == 72.0
    assert scores.get("market_score")            == 78.0
    assert scores.get("market_saturation_score") == 55.0
    assert scores.get("research_maturity_score") == 68.0
    assert scores.get("novelty_score")           == 74.0
    assert scores.get("risk_score")              == 38.0


# ─── Fire-and-forget: never raises ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_log_agent_complete_does_not_raise_on_none_result():
    await log_agent_complete("job-6", "Agent", 1.0, None)   # must not raise


@pytest.mark.asyncio
async def test_log_agent_complete_does_not_raise_on_garbage():
    await log_agent_complete("job-7", "Agent", 1.0, "not a dict")


@pytest.mark.asyncio
async def test_log_agent_error_does_not_raise():
    await log_agent_error("job-8", "Agent", 0.1, None)


@pytest.mark.asyncio
async def test_log_agent_start_does_not_raise():
    await log_agent_start("job-9", None)


@pytest.mark.asyncio
async def test_log_pipeline_complete_does_not_raise_on_empty_state():
    await log_pipeline_complete("job-10", 0.0, {})


@pytest.mark.asyncio
async def test_all_log_functions_silent_when_file_logger_fails():
    """Even if the file logger raises, the functions must not propagate."""
    def boom(msg):
        raise OSError("disk full")

    with patch.object(agent_logger_module, "_file_logger") as mock_logger:
        mock_logger.info = boom
        await log_agent_complete("job-11", "Agent", 1.0, {"score": 42})
        await log_agent_error("job-12", "Agent", 0.5, "err")
        await log_agent_start("job-13", "Agent")
        await log_pipeline_complete("job-14", 5.0, {})
    # If we reach here, no exception was raised — test passes


# ─── Supabase disabled ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_log_complete_works_when_supabase_not_configured():
    with patch("services.agent_logger._supabase_configured", return_value=False):
        with patch.object(agent_logger_module, "_file_logger") as mock_logger:
            written = []
            mock_logger.info = lambda msg: written.append(msg)
            await log_agent_complete("job-15", "Agent", 1.0, _research_result())

    assert len(written) == 1  # file log still written


@pytest.mark.asyncio
async def test_supabase_failure_does_not_propagate():
    """Even if Supabase insert raises, the function must not propagate."""
    with patch("services.agent_logger._persist_to_supabase", new=AsyncMock(side_effect=Exception("DB down"))):
        with patch.object(agent_logger_module, "_file_logger") as mock_logger:
            mock_logger.info = lambda msg: None
            await log_agent_complete("job-16", "Agent", 1.0, _research_result())
    # Reaching here means no exception was raised


# ─── Record field validation ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_complete_record_has_output_keys():
    with patch.object(agent_logger_module, "_file_logger") as mock_logger:
        written = []
        mock_logger.info = lambda msg: written.append(msg)
        result = {"market_overview": "big", "sources": ["url1"]}
        await log_agent_complete("job-17", "Research Agent", 2.0, result)

    record = json.loads(written[0])
    assert set(result.keys()).issubset(set(record["output_keys"]))


@pytest.mark.asyncio
async def test_error_record_truncates_long_message():
    long_error = "x" * 1000
    with patch.object(agent_logger_module, "_file_logger") as mock_logger:
        written = []
        mock_logger.info = lambda msg: written.append(msg)
        await log_agent_error("job-18", "Agent", 1.0, long_error)

    record = json.loads(written[0])
    assert len(record["error_msg"]) <= 500


@pytest.mark.asyncio
async def test_timestamp_is_iso_format():
    with patch.object(agent_logger_module, "_file_logger") as mock_logger:
        written = []
        mock_logger.info = lambda msg: written.append(msg)
        await log_agent_start("job-19", "Agent")

    record = json.loads(written[0])
    from datetime import datetime
    # Should not raise
    datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
