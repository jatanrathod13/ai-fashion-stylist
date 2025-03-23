"""
Simple database connection test script.
"""

import asyncio
from app.database import engine
from sqlalchemy import text

async def test_connection():
    """Test the database connection."""
    print("Testing database connection...")
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(f"Database connection test: {result.scalar() == 1}")
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_connection()) 