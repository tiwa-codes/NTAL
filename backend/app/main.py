from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api.v1.endpoints import router as api_router
from .core.database import engine, Base
from .core.redis_client import get_redis, close_redis
from .models.models import Provider, Encounter, Callback


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup/shutdown)."""
    # Startup: Create database tables and initialize Redis
    Base.metadata.create_all(bind=engine)
    await get_redis()
    yield
    # Shutdown: Close Redis connection
    await close_redis()


app = FastAPI(
    title="NTAL Telehealth API",
    description="API for NTAL inclusive telehealth platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "NTAL Telehealth API",
        "docs": "/api/docs",
        "version": "1.0.0"
    }
