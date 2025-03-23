"""
Database Migration Helper

This script helps transition from manual SQLAlchemy table creation to Alembic migrations.
It provides utilities to:
1. Mark existing migrations as applied without running them (if tables already exist)
2. Reset the database entirely and apply migrations from scratch
"""

import asyncio
import argparse
import os
import subprocess
from sqlalchemy import text
import sqlite3

from app.database import engine
from app.config import settings

async def test_connection():
    """Test the database connection and report status."""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Database connection test: {result.scalar() == 1}")
            return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

def reset_database():
    """Delete the SQLite database file if it exists."""
    db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    if db_path.startswith("./"):
        db_path = db_path[2:]
    
    if os.path.exists(db_path):
        print(f"Removing existing database file: {db_path}")
        os.remove(db_path)
        print("Database file removed.")
    else:
        print("No existing database file found.")

def mark_migrations_as_applied():
    """Mark the existing migrations as applied without running them."""
    try:
        # Create alembic_version table if it doesn't exist
        db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
        if db_path.startswith("./"):
            db_path = db_path[2:]
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)")
        
        # Get the latest migration version from alembic
        migrations = subprocess.check_output(["alembic", "history"]).decode().strip().split("\n")
        if migrations:
            latest_version = migrations[0].strip().split("->")[0].strip()
            print(f"Latest migration version: {latest_version}")
            
            # Insert this version into alembic_version
            cursor.execute("DELETE FROM alembic_version")
            cursor.execute("INSERT INTO alembic_version (version_num) VALUES (?)", (latest_version,))
            conn.commit()
            print("Migration marked as applied.")
        else:
            print("No migrations found.")
            
        conn.close()
    except Exception as e:
        print(f"Error marking migrations as applied: {e}")

async def run_migrations():
    """Run Alembic migrations."""
    try:
        print("Running database migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Database migrations completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")

async def main():
    """Main function to handle command line arguments and run the appropriate actions."""
    parser = argparse.ArgumentParser(description="Database Migration Helper")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--reset", action="store_true", help="Reset the database and apply migrations from scratch")
    group.add_argument("--mark-applied", action="store_true", help="Mark existing migrations as applied without running them")
    group.add_argument("--run-migrations", action="store_true", help="Run migrations without resetting the database")
    
    args = parser.parse_args()
    
    if args.reset:
        reset_database()
        await run_migrations()
    elif args.mark_applied:
        if await test_connection():
            mark_migrations_as_applied()
        else:
            print("Cannot mark migrations as applied: database connection failed.")
    elif args.run_migrations:
        await run_migrations()

if __name__ == "__main__":
    asyncio.run(main()) 