from __future__ import annotations

from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel

# Create a FastAPI instance
app = FastAPI()

# Pydantic model for test request data
class TestData(BaseModel):
    value: int

# Root endpoint for health check
@app.get('/')
async def read_root():
    return {'message': 'Test API is running'}

# Endpoint to test simple math operation
@app.post('/test-sum')
async def test_sum(data: TestData):
    """
    This endpoint receives an integer and returns the sum of that value and a fixed number.
    """
    return {'sum': data.value + 5}

# Endpoint to simulate error handling
@app.get('/test-error')
async def test_error():
    """
    This endpoint raises an HTTPException for testing error handling.
    """
    raise HTTPException(status_code=400, detail='This is a test error')

# Endpoint for testing query parameters
@app.get('/test-query')
async def test_query(param1: str, param2: int):
    """
    This endpoint accepts two query parameters for testing.
    """
    return {'param1': param1, 'param2': param2}
