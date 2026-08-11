from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.middleware import RateLimiter, rate_limiter


def test_rate_limiter_unit_logic():
    limiter = RateLimiter(max_requests=16, window_seconds=60.0)
    user_key = "test_user_unit"

    # First 16 requests should be allowed
    for i in range(16):
        allowed, remaining, _ = limiter.is_allowed(user_key)
        assert allowed is True, f"Request {i+1} should be allowed"

    # 17th request should be blocked
    allowed, remaining, reset_in = limiter.is_allowed(user_key)
    assert allowed is False, "17th request within 1 minute should be blocked"
    assert remaining == 0
    assert reset_in > 0


def test_rate_limiter_endpoint_429(monkeypatch):
    client = TestClient(app)

    # Use a unique user_id to isolate from other tests
    user_id = "rate_limit_integration_user"
    payload = {
        "user_id": user_id,
        "session_id": "sess_rate_limit",
        "feature": "qa",
        "message": "Testing rate limit",
    }

    # Reset rate_limiter state for this test key
    from app.pii import hash_user_id
    key = hash_user_id(user_id)
    rate_limiter.requests[key] = []

    # Send 16 requests (all HTTP 200)
    for i in range(16):
        res = client.post("/chat", json=payload)
        assert res.status_code == 200, f"Request {i+1} failed unexpectedly with status {res.status_code}"

    # 17th request must fail with HTTP 429 Too Many Requests
    res_17 = client.post("/chat", json=payload)
    assert res_17.status_code == 429
    assert "Rate limit exceeded" in res_17.json()["detail"]
    assert "Retry-After" in res_17.headers
