"""
Security tests: input validation, secret output scanning, mock mode.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app
from services.secret_scanner import assert_clean, scan

client = TestClient(app)

_LONG_IDEA = "An AI-powered healthcare startup" + " x" * 600  # > 1000 chars
_CONTROL_CHAR_IDEA = "An AI startup\x00 with null byte" + " more text" * 2


# ── Input validation ──────────────────────────────────────────────────────────

class TestInputValidation:
    def test_idea_too_short_returns_422(self):
        res = client.post("/research/start", json={"idea": "short"})
        assert res.status_code == 422

    def test_idea_too_long_returns_422(self):
        res = client.post("/research/start", json={"idea": _LONG_IDEA})
        assert res.status_code == 422

    def test_extra_field_in_request_rejected(self):
        """extra='forbid' must reject unknown fields."""
        res = client.post(
            "/research/start",
            json={
                "idea": "An AI-powered healthcare startup that automates triage",
                "user_id": "injected-user-id",  # must be rejected
            },
        )
        assert res.status_code == 422

    def test_extra_user_id_in_scenario_rejected(self):
        import uuid
        fake_id = str(uuid.uuid4())
        res = client.post(
            f"/research/{fake_id}/scenario",
            json={
                "scenario": {},
                "user_id": "injected-user-id",  # must be rejected
            },
        )
        assert res.status_code == 422

    def test_invalid_uuid_in_path_returns_422(self):
        res = client.get("/research/not-a-valid-uuid/status")
        assert res.status_code == 422

    def test_ask_question_too_short(self):
        import uuid
        fake_id = str(uuid.uuid4())
        res = client.post(f"/research/{fake_id}/ask", json={"question": "hi"})
        assert res.status_code == 422

    def test_ask_question_too_long(self):
        import uuid
        fake_id = str(uuid.uuid4())
        res = client.post(
            f"/research/{fake_id}/ask",
            json={"question": "x" * 600},
        )
        assert res.status_code == 422

    def test_extra_field_in_ask_rejected(self):
        import uuid
        fake_id = str(uuid.uuid4())
        res = client.post(
            f"/research/{fake_id}/ask",
            json={"question": "What is the market size?", "user_id": "evil"},
        )
        assert res.status_code == 422

    def test_no_user_id_in_start_research_body(self):
        """Confirm user_id field does not appear in ResearchRequest schema."""
        from schemas.models import ResearchRequest
        assert not hasattr(ResearchRequest.model_fields.get("user_id", None), "default"), \
            "user_id must not be a field in ResearchRequest"
        assert "user_id" not in ResearchRequest.model_fields


# ── Secret scanner unit tests ──────────────────────────────────────────────────

class TestSecretScanner:
    def test_clean_text_passes(self):
        assert scan("The market size is $50 billion.") is None

    def test_fireworks_key_detected(self):
        assert scan("My key is fw_NEzvW8wt8MQStiaJKbYSPKabc123") is not None

    def test_openai_key_detected(self):
        assert scan("sk-abcdefghijklmnopqrstuvwxyz123456") is not None

    def test_jwt_token_detected(self):
        # A real JWT starts with eyJ...
        assert scan("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsImV4cCI6MTc4MzM1Njg3Nn0.XXXX") is not None

    def test_private_key_detected(self):
        assert scan("-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASC") is not None

    def test_assert_clean_raises_on_secret(self):
        with pytest.raises(ValueError, match="Output blocked"):
            assert_clean("Use fw_NEzvW8wt8MQStiaJKbYSPKabc123 as the key", "test_agent")

    def test_assert_clean_passes_clean_text(self):
        assert_clean("The TAM is $5B and growing at 15% CAGR.", "test_agent")


# ── Mock mode ─────────────────────────────────────────────────────────────────

class TestMockMode:
    def test_mock_allowed_when_flag_true(self, monkeypatch):
        from services import tavily_client
        monkeypatch.setattr(tavily_client.settings, "TAVILY_API_KEY", "")
        monkeypatch.setattr(tavily_client.settings, "ALLOW_MOCK_SEARCH", True)
        # Should return mock results without raising
        assert tavily_client._is_mock() is True

    def test_mock_blocked_when_flag_false(self, monkeypatch):
        from services import tavily_client
        monkeypatch.setattr(tavily_client.settings, "TAVILY_API_KEY", "")
        monkeypatch.setattr(tavily_client.settings, "ALLOW_MOCK_SEARCH", False)
        with pytest.raises(RuntimeError, match="ALLOW_MOCK_SEARCH"):
            tavily_client._is_mock()

    def test_real_key_skips_mock_check(self, monkeypatch):
        from services import tavily_client
        monkeypatch.setattr(tavily_client.settings, "TAVILY_API_KEY", "tvly-real-key")
        monkeypatch.setattr(tavily_client.settings, "ALLOW_MOCK_SEARCH", False)
        assert tavily_client._is_mock() is False


# ── Rate limiting ──────────────────────────────────────────────────────────────

class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_rate_limit_enforced(self):
        from services.rate_limiter import _SlidingWindow
        from fastapi import HTTPException
        rl = _SlidingWindow()
        for _ in range(3):
            await rl.check("test-user:op", limit=3, window_seconds=60)
        with pytest.raises(HTTPException) as exc_info:
            await rl.check("test-user:op", limit=3, window_seconds=60)
        assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_different_users_independent(self):
        from services.rate_limiter import _SlidingWindow
        rl = _SlidingWindow()
        for _ in range(3):
            await rl.check("user-x:op", limit=3, window_seconds=60)
        # user-y should not be affected
        await rl.check("user-y:op", limit=3, window_seconds=60)
