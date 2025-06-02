"""
FastAPI application for 3D Printing Anomaly Detection System.

This module sets up the main FastAPI application with all the necessary
middleware, routers, and configurations.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn

from .endpoints import images, slicer_settings, parts, inference
from .core.config import settings

# Create FastAPI application instance
app = FastAPI(
    title="3D Printing Anomaly Detection API",
    description="API for managing 3D printing data and running anomaly detection",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    images.router, prefix=f"{settings.API_V1_STR}/images", tags=["images"]
)
app.include_router(
    slicer_settings.router,
    prefix=f"{settings.API_V1_STR}/slicer-settings",
    tags=["slicer-settings"],
)
app.include_router(parts.router, prefix=f"{settings.API_V1_STR}/parts", tags=["parts"])
app.include_router(
    inference.router, prefix=f"{settings.API_V1_STR}/inference", tags=["inference"]
)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "3D Printing Anomaly Detection API is running",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
