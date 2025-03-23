#!/usr/bin/env python3
"""
Simple script to reset a user's password in the database using direct SQL.
"""

import argparse
import sqlite3
import bcrypt
from pathlib import Path

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password with the salt
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Return the hashed password as a string
    return hashed.decode('utf-8')

def reset_password(email: str, new_password: str, db_path: str = "fashion_stylist.db"):
    """Reset a user's password using direct SQL"""
    # Ensure the database file exists
    if not Path(db_path).exists():
        print(f"Database file '{db_path}' not found.")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the user exists
        cursor.execute("SELECT id, username FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"User with email '{email}' not found.")
            return
        
        user_id, username = user
        
        # Hash the new password
        hashed_password = hash_password(new_password)
        
        # Update the user's password
        cursor.execute(
            "UPDATE users SET hashed_password = ? WHERE id = ?",
            (hashed_password, user_id)
        )
        
        # Commit the changes
        conn.commit()
        
        print(f"Password for user '{username}' (ID: {user_id}) has been reset.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        conn.rollback()
    
    finally:
        # Close the connection
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset a user's password")
    parser.add_argument("email", help="Email of the user to reset password for")
    parser.add_argument("password", help="New password")
    parser.add_argument("--db", default="fashion_stylist.db", help="Path to the database file")
    
    args = parser.parse_args()
    
    reset_password(args.email, args.password, args.db) 