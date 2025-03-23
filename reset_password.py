#!/usr/bin/env python3
"""
Reset a user's password in the database.
"""

import asyncio
import argparse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.dependencies.auth import get_password_hash

async def reset_password(email: str, new_password: str):
    """Reset a user's password"""
    async for db in get_db():
        # Try to find the user by email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"User with email '{email}' not found.")
            return
        
        # Hash the new password
        hashed_password = get_password_hash(new_password)
        
        # Update the user's password
        user.hashed_password = hashed_password
        
        # Commit the changes
        await db.commit()
        
        print(f"Password for user '{user.username}' ({email}) has been reset.")
        # Only process the first iteration of the generator
        break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset a user's password")
    parser.add_argument("email", help="Email of the user to reset password for")
    parser.add_argument("password", help="New password")
    
    args = parser.parse_args()
    
    asyncio.run(reset_password(args.email, args.password)) 