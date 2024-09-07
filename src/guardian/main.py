from fastAPI import FastAPI
from app.interface.api import router

app = FastAPI(title="Guardian API")

# Include the router
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0", port=8000)
