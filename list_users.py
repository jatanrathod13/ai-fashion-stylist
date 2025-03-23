#!/usr/bin/env python3
"""
List users from the database.
"""

import asyncio
from sqlalchemy import select
from app.database import get_db
from app.models.user import User

async def list_users():
    """List all users in the database"""
    async for db in get_db():
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            print("No users found in the database.")
            return
            
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"- Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  ID: {user.id}")
            print(f"  Active: {user.is_active}")
            print()
        
        # Only process the first iteration of the generator
        break

if __name__ == "__main__":
    asyncio.run(list_users()) 