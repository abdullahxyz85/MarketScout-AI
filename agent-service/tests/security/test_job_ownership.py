"""
Security tests: job ownership enforcement.

Tests cover:
- User A creates Job A
- User A can access Job A
- User B cannot access Job A (returns 404, not 403)
- Anonymous caller cannot access Job A when auth is enabled
- Invalid UUID returns 422
- Ownership is enforced on all sensitive routes
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from fastapi.testclient import TestClient

import router as router_module
from main import app
from schemas.models import JobStatus

client = TestClient(app)

_SECRET = "ownership-test-secret"
_ALG = "HS256"
_IDEA = "An AI platform that automates market research for startups using LLMs and web search"


def _token(user_id: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=1)
    return jwt.encode({"sub": user_id, "exp": exp}, _SECRET, algorithm=_ALG)


def _cookies(user_id: str) -> dict:
    return {"access_token": _token(user_id)}


def _inject_job(job_id: str, owner: str, completed: bool = True) -> None:
    """Directly inject a job into the in-memory registry for testing."""
    router_module._jobs[job_id] = {
        "status": JobStatus.COMPLETED if completed else JobStatus.RUNNING,
        "created_at": datetime.utcnow().isoformat(),
        "idea": _IDEA,
        "industry": "SaaS",
        "result": {"report": {"executive_summary": "Test summary"}} if completed else None,
        "owner_user_id": owner,
    }


@pytest.fixture(autouse=True)
def _enable_auth_and_patch(monkeypatch):
    """Enable strict auth for all ownership tests."""
    import config
    import services.auth_guard as auth_guard_mod
    monkeypatch.setattr(config.settings, "AGENT_AUTH_ENABLED", True)
    monkeypatch.setattr(config.settings, "JWT_SECRET", _SECRET)
    monkeypatch.setattr(auth_guard_mod.settings, "AGENT_AUTH_ENABLED", True)
    monkeypatch.setattr(auth_guard_mod.settings, "JWT_SECRET", _SECRET)


class TestJobOwnership:
    def test_owner_can_access_own_status(self):
        job_id = str(uuid.uuid4())
        _inject_job(job_id, "user-a")
        res = client.get(f"/research/{job_id}/status", cookies=_cookies("user-a"))
        assert res.status_code == 200

    def test_other_user_cannot_access_job_status(self):
        """User B gets 404, not 403, to avoid revealing the job exists."""
        job_id = str(uuid.uuid4())
        _inject_job(job_id, "user-a")
        res = client.get(f"/research/{job_id}/status", cookies=_cookies("user-b"))
        assert res.status_code == 404

    def test_unauthenticated_cannot_access_job_status(self):
        job_id = str(uuid.uuid4())
        _inject_job(job_id, "user-a")
        res = client.get(f"/research/{job_id}/status")
        assert res.status_code == 401

    def test_owner_can_get_result(self):
        job_id = str(uuid.uuid4())
        _inject_job(job_id, "user-a")
        res = client.get(f"/research/{job_id}/result", cookies=_cookies("user-a"))
        assert res.status_code == 200

    def test_other_user_cannot_get_result(self):
        job_id = str(uuid.uuid4())
        _inject_job(job_id, "user-a")
        res = client.get(f"/research/{job_id}/result", cookies=_cookies("user-b"))
        assert res.status_code == 404

    def test_invalid_uuid_returns_422(self):
        res = client.get("/research/not-a-uuid/status", cookies=_cookies("user-a"))
        assert res.status_code == 422

    def test_invalid_uuid_for_result(self):
        res = client.get("/research/abc/result", cookies=_cookies("user-a"))
        assert res.status_code == 422

    def test_unknown_job_id_returns_404(self):
        fake_id = str(uuid.uuid4())
        res = client.get(f"/research/{fake_id}/status", cookies=_cookies("user-a"))
        assert res.status_code == 404

    def test_other_user_cannot_download_pdf(self):
        job_id = str(uuid.uuid4())
        _inject_job(job_id, "user-a")
        res = client.get(f"/research/{job_id}/report/pdf", cookies=_cookies("user-b"))
        assert res.status_code == 404

    def test_other_user_cannot_run_scenario(self):
        job_id = str(uuid.uuid4())
        _inject_job(job_id, "user-a")
        res = client.post(
            f"/research/{job_id}/scenario",
            json={"scenario": {}},
            cookies=_cookies("user-b"),
        )
        assert res.status_code == 404

    def test_other_user_cannot_ask_question(self):
        job_id = str(uuid.uuid4())
        _inject_job(job_id, "user-a")
        res = client.post(
            f"/research/{job_id}/ask",
            json={"question": "What is the market size?"},
            cookies=_cookies("user-b"),
        )
        assert res.status_code == 404
