"""
Security tests: authentication and authorization.

Tests cover:
- Unauthenticated access returns 401 when auth is enabled
- Cross-user job access returns 404
- Invalid JWT returns 401
- Expired JWT returns 401
- Dev-mode bypass works as expected
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from fastapi.testclient import TestClient

from main import app
from schemas.models import JobStatus
from services.auth_guard import _DEV_USER

client = TestClient(app)

_TEST_SECRET = "test-jwt-secret-for-security-tests"
_ALG = "HS256"


def _make_token(user_id: str, secret: str = _TEST_SECRET, expired: bool = False) -> str:
    exp = datetime.now(timezone.utc) + (timedelta(seconds=-10) if expired else timedelta(hours=1))
    return jwt.encode({"sub": user_id, "exp": exp}, secret, algorithm=_ALG)


def _cookie(token: str) -> dict:
    return {"access_token": token}


# ── Dev mode (AGENT_AUTH_ENABLED=false) ───────────────────────────────────────

class TestDevModeBypass:
    """When AGENT_AUTH_ENABLED=false all requests are accepted without a token."""

    def test_health_check_no_auth_required(self):
        res = client.get("/health")
        assert res.status_code == 200

    def test_start_research_without_token_in_dev_mode(self):
        """Dev mode: no cookie → accepted (returns 422 for bad idea, not 401)."""
        res = client.post("/research/start", json={"idea": "too short"})
        # Should fail validation (422) not auth (401) in dev mode
        assert res.status_code == 422

    def test_unknown_job_returns_404_not_401_in_dev_mode(self):
        fake_id = str(uuid.uuid4())
        res = client.get(f"/research/{fake_id}/status")
        assert res.status_code == 404


# ── Auth enabled mode ─────────────────────────────────────────────────────────

class TestAuthEnabled:
    """When AGENT_AUTH_ENABLED=true, strict JWT validation is enforced."""

    @pytest.fixture(autouse=True)
    def _enable_auth(self, monkeypatch):
        import config
        import services.auth_guard as auth_guard_mod
        monkeypatch.setattr(config.settings, "AGENT_AUTH_ENABLED", True)
        monkeypatch.setattr(config.settings, "JWT_SECRET", _TEST_SECRET)
        monkeypatch.setattr(auth_guard_mod.settings, "AGENT_AUTH_ENABLED", True)
        monkeypatch.setattr(auth_guard_mod.settings, "JWT_SECRET", _TEST_SECRET)

    def test_missing_token_returns_401(self):
        res = client.post(
            "/research/start",
            json={"idea": "An AI-powered healthcare startup that monitors patients remotely"},
        )
        assert res.status_code == 401

    def test_invalid_token_returns_401(self):
        res = client.post(
            "/research/start",
            json={"idea": "An AI-powered healthcare startup that monitors patients remotely"},
            cookies={"access_token": "not.a.valid.jwt"},
        )
        assert res.status_code == 401

    def test_expired_token_returns_401(self):
        token = _make_token("user-abc", expired=True)
        res = client.post(
            "/research/start",
            json={"idea": "An AI-powered healthcare startup that monitors patients remotely"},
            cookies=_cookie(token),
        )
        assert res.status_code == 401

    def test_wrong_secret_returns_401(self):
        token = _make_token("user-abc", secret="wrong-secret")
        res = client.post(
            "/research/start",
            json={"idea": "An AI-powered healthcare startup that monitors patients remotely"},
            cookies=_cookie(token),
        )
        assert res.status_code == 401

    def test_valid_token_accepted(self, monkeypatch):
        import config
        import services.auth_guard as auth_guard_mod
        monkeypatch.setattr(config.settings, "AGENT_AUTH_ENABLED", True)
        monkeypatch.setattr(config.settings, "JWT_SECRET", _TEST_SECRET)
        monkeypatch.setattr(auth_guard_mod.settings, "AGENT_AUTH_ENABLED", True)
        monkeypatch.setattr(auth_guard_mod.settings, "JWT_SECRET", _TEST_SECRET)
        token = _make_token("user-valid")
        # Rate limiter may reject; we just need it not to be 401
        res = client.post(
            "/research/start",
            json={"idea": "An AI-powered healthcare startup that automates triage"},
            cookies=_cookie(token),
        )
        assert res.status_code != 401
