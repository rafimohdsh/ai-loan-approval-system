from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import sys
import os
from pathlib import Path
import logging
from .logging_config import setup_logging, get_logger

# Configure structured logging
setup_logging()
logger = get_logger(__name__)

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from . import api
from .database import engine
from .models import Base

# Create tables
logger.info("Creating database tables")
Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Trusted hosts middleware
allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# Add CORS middleware with restricted origins
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8501").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
logger.info("Including API routers")
app.include_router(api.endpoints.loans.router)
app.include_router(api.endpoints.reviewer.router)
app.include_router(api.endpoints.appeal.router)
app.include_router(api.endpoints.settings.router)
logger.info("API routers registered successfully")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {"status": "healthy", "app": settings.APP_NAME}


@app.get("/")
async def root():
    """Root endpoint."""
    logger.debug("Root endpoint accessed")
    return {"message": "Welcome to Agentic Loan Approval System"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT
    )
