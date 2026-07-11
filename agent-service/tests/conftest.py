import os

import pytest

# Ensure Settings() can construct even when no .env / real credentials are present
# (e.g. in CI). Required fields get a harmless placeholder; optional ones stay unset
# so services correctly fall back to their mock/no-op paths.
os.environ.setdefault("FIREWORKS_API_KEY", "test-key")


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate-limiter windows before every test to avoid cross-test contamination."""
    from services.rate_limiter import limiter
    limiter.reset()
    yield
    limiter.reset()
