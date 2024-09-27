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

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Check if this is an HTTP request
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        # Create a request object from scope
        request = Request(scope, receive=receive)

        # Start time for calculating latency
        start_time = time.time()

        # Capture the status code from the response
        response_status = {'status_code': 500}  # Default to 500 in case of an issue

        async def send_wrapper(message):
            # Intercept the response message to capture the status code
            if message['type'] == 'http.response.start':
                response_status['status_code'] = message['status']

            # Call the original send function
            await send(message)

        # Call the next middleware or route handler
        await self.app(scope, receive, send_wrapper)

        # Calculate request latency
        latency = time.time() - start_time

        # Get request details
        method = request.method
        endpoint = request.url.path
        status_code = str(response_status['status_code'])

        # Update Prometheus metrics
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
