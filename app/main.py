# app/main.py
from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from app.interfaces.api import router

app = FastAPI(title='Guardian Security Gateway')

# Include the API router
app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080, log_level='error')
