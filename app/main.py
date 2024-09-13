# app/main.py
from fastapi import FastAPI
from app.interfaces.api import router

app = FastAPI(title="Guardian Security Gateway")

# Include the API router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)