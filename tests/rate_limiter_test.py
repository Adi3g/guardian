# tests/test_rate_limiter.py
from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.core.services.rate_limiter import RateLimiter

def test_rate_limiter_allows_requests_within_limit():
    rate_limiter = RateLimiter(max_requests=5, ban_duration=300)
    client_ip = '192.168.1.10'

    # Simulate 5 requests within the limit
    for _ in range(5):
        assert rate_limiter.is_allowed(client_ip) == True

def test_rate_limiter_blocks_after_exceeding_limit():
    rate_limiter = RateLimiter(max_requests=5, ban_duration=300)
    client_ip = '192.168.1.10'

    # Simulate 6 requests, where the 6th should be blocked
    for _ in range(5):
        assert rate_limiter.is_allowed(client_ip) == True

    with pytest.raises(HTTPException) as excinfo:
        rate_limiter.is_allowed(client_ip)

    assert excinfo.value.status_code == 429
    assert 'Too many requests' in str(excinfo.value.detail)

# def test_rate_limiter_respects_ban_duration():
#     rate_limiter = RateLimiter(max_requests=1, ban_duration=1)  # 1 second ban
#     client_ip = '192.168.1.10'

#     # First request should be allowed
#     assert rate_limiter.is_allowed(client_ip) == True

#     # Second request should be blocked
#     with pytest.raises(HTTPException) as excinfo:
#         rate_limiter.is_allowed(client_ip)

#     assert excinfo.value.status_code == 429

#     # Wait for the ban duration to expire
#     import time
#     time.sleep(1.1)  # Sleep slightly longer than ban duration

#     # Request should be allowed again
#     assert rate_limiter.is_allowed(client_ip) == True
