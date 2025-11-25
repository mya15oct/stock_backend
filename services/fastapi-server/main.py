from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import quote_router, financial_router
from config.settings import settings
from streaming.manager import manager
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    manager.start()
    yield
    # Shutdown
    logger.info("Shutting down...")
    manager.stop()

app = FastAPI(
    title="Stock Data API",
    description="Stock Analytics API with Real Financial Data",
    version="2.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Should be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(quote_router.router)
app.include_router(financial_router.router)

@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Stock Data API is running",
        "config": {
            "db_host": settings.DB_HOST,
            "redis_enabled": bool(settings.REDIS_HOST)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
