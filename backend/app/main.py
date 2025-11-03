from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.endpoints import router as api_router
from .core.database import engine, Base
from .models.models import Provider, Encounter

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NTAL Telehealth API",
    description="API for NTAL inclusive telehealth platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
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
