
import pytest
from fastapi import HTTPException

from src.security import rate_limit


# Clear request history before each test.
@pytest.fixture(autouse=True)
def clear_request_history():
    rate_limit.request_history.clear()


def test_requests_within_limit_are_allowed(monkeypatch):
    """Verify that requests within the limit are allowed."""

    monkeypatch.setattr(rate_limit.time, "time", lambda: 1000)

    rate_limit.check_rate_limit("client_A", max_requests=3)
    rate_limit.check_rate_limit("client_A", max_requests=3)
    rate_limit.check_rate_limit("client_A", max_requests=3)


def test_exceeding_limit_returns_429(monkeypatch):
    """Verify that exceeding the limit returns HTTP 429."""

    monkeypatch.setattr(rate_limit.time, "time", lambda: 1000)

    for _ in range(3):
        rate_limit.check_rate_limit("client_A", max_requests=3)

    with pytest.raises(HTTPException) as error:
        rate_limit.check_rate_limit("client_A", max_requests=3)

    assert error.value.status_code == 429
    assert error.value.headers["Retry-After"] == "61"


def test_expired_requests_are_removed(monkeypatch):
    """Verify that expired requests no longer count toward the limit."""

    current_time = [1000]

    monkeypatch.setattr(
        rate_limit.time,
        "time",
        lambda: current_time[0],
    )

    rate_limit.check_rate_limit("client_A", max_requests=2)
    rate_limit.check_rate_limit("client_A", max_requests=2)

    # Move time forward beyond the 60-second window.
    current_time[0] = 1061

    # This request should now be allowed.
    rate_limit.check_rate_limit("client_A", max_requests=2)
