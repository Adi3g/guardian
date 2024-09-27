# app/middleware/metrics_middleware.py
from __future__ import annotations

import time

from prometheus_client import Counter
from prometheus_client import Histogram
from starlette.requests import Request
from starlette.responses import Response

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    'app_requests_total', 'Total number of requests',
    ['method', 'endpoint', 'http_status'],
)

REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds', 'Request latency', ['method', 'endpoint'],
)

class MetricsMiddleware:
    """
    Middleware to track Prometheus metrics for request count and response time.
    """

    async def __call__(self, request: Request, call_next):
        # Start time for calculating latency
        start_time = time.time()

        # Process the request
        response: Response = await call_next(request)

        # Calculate request latency
        latency = time.time() - start_time

        # Get request details
        method = request.method
        endpoint = request.url.path
        status_code = str(response.status_code)

        # Update Prometheus metrics
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)

        return response
