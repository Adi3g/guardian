# app/core/services/rate_limiter.py

from fastapi import HTTPException
from time import time
from collections import defaultdict

class RateLimiter:
    """
    RateLimiter class to handle request rate limiting per client IP.
    """

    def __init__(self, max_requests: int, ban_duration: int):
        """
        Initialize the RateLimiter.

        :param max_requests: Maximum number of requests allowed per minute
        :param ban_duration: Duration (in seconds) to ban IPs that exceed the limit
        """
        self.max_requests = max_requests
        self.ban_duration = ban_duration
        self.requests = defaultdict(list)
        self.banned_ips = {}

    def is_allowed(self, client_ip: str) -> bool:
        """
        Check if the request from the client IP is allowed based on rate limiting rules.

        :param client_ip: The IP address of the client
        :return: True if allowed, False if rate limit exceeded
        """
        current_time = time()

        # Check if IP is banned
        if client_ip in self.banned_ips and current_time < self.banned_ips[client_ip]:
            raise HTTPException(status_code=429, detail="Too many requests. You are temporarily banned.")

        # Clean up old requests
        self.requests[client_ip] = [t for t in self.requests[client_ip] if current_time - t < 60]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            self.banned_ips[client_ip] = current_time + self.ban_duration
            raise HTTPException(status_code=429, detail="Too many requests. You are temporarily banned.")

        # Log the request
        self.requests[client_ip].append(current_time)
        return True
