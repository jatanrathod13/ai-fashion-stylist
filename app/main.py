"""
Main application module.

This module serves as the entry point for the AI Fashion Stylist API.
It configures the FastAPI application, includes all routers, and sets up middleware.
"""

import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import routers

# Create the FastAPI application
app = FastAPI(
    title="AI Fashion Stylist API",
    description="API for AI-powered fashion recommendations and style analysis",
    version="0.1.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if it doesn't exist
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Mount static files for image serving if needed
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include all routers
for router in routers:
    app.include_router(router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint that returns API information.
    """
    return {
        "name": "AI Fashion Stylist API",
        "version": "0.1.0",
        "documentation": "/docs",
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to provide consistent error responses.
    """
    # Log the exception here (implementation depends on your logging strategy)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Execute tasks when the application starts.
    """
    # Any startup tasks can be added here
    pass


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute tasks when the application shuts down.
    """
    # Any cleanup tasks can be added here
    pass

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 