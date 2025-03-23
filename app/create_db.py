"""
Database initialization script.

This script sets up the database by executing Alembic migrations.
Run this script before starting the application for the first time.
"""

import asyncio
import subprocess
import os
from sqlalchemy import text

from app.database import engine
from app.models.base import Base

async def init_db():
    """Initialize the database by running Alembic migrations."""
    print("Initializing database...")
    
    # Test database connection
    async with engine.begin() as conn:
        try:
            result = await conn.execute(text("SELECT 1"))
            print(f"Database connection test: {result.scalar() == 1}")
        except Exception as e:
            print(f"Database connection error: {e}")
            return
    
    # Run Alembic migrations
    try:
        print("Running database migrations...")
        # Use the upgrade command to apply all migrations
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Database migrations completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")
        return
    
    print("Database initialization completed!")

if __name__ == "__main__":
    """Run the database initialization script."""
    asyncio.run(init_db()) 