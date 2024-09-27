# app/main.py
from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest

from app.interfaces.api import router
from app.middlewares.metrics_middleware import MetricsMiddleware

app = FastAPI(title='Guardian Security Gateway')

# Add MetricsMiddleware to capture metrics on every request
app.add_middleware(MetricsMiddleware)


# Prometheus Metrics endpoint
@app.get('/metrics')
def metrics():
    """
    Endpoint to expose Prometheus metrics for scraping.
    """
    return PlainTextResponse(generate_latest())


# Include the API router
app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080, log_level='error')
