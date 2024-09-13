# app/main.py
from fastapi import FastAPI
import uvicorn
from app.interfaces.api import router

app = FastAPI(title="Guardian Security Gateway")

# Include the API router
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
