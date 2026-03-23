"""Tests for rate limiter."""
from app.middleware.rate_limiter import InMemoryRateLimiter


def test_allows_under_limit():
    limiter = InMemoryRateLimiter(max_requests=5, window_seconds=60)
    for _ in range(5):
        assert limiter.is_allowed("client1") is True

def test_blocks_over_limit():
    limiter = InMemoryRateLimiter(max_requests=3, window_seconds=60)
    for _ in range(3):
        limiter.is_allowed("client1")
    assert limiter.is_allowed("client1") is False

def test_different_clients_independent():
    limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)
    limiter.is_allowed("client1")
    limiter.is_allowed("client1")
    assert limiter.is_allowed("client1") is False
    assert limiter.is_allowed("client2") is True

def test_remaining_count():
    limiter = InMemoryRateLimiter(max_requests=10, window_seconds=60)
    limiter.is_allowed("client1")
    limiter.is_allowed("client1")
    assert limiter.get_remaining("client1") == 8

def test_zero_remaining_when_full():
    limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)
    limiter.is_allowed("c")
    limiter.is_allowed("c")
    assert limiter.get_remaining("c") == 0
