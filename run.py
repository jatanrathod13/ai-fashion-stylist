"""
Application runner script.

This script provides a convenient way to start the application.
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    """Run the application."""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    ) 