#!/usr/bin/env python3
"""
Set a user as admin by email
"""
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

async def set_admin(email: str):
    """Set user as admin"""
    mongodb_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME", "german_ai")
    
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[db_name]
    
    # Update user to admin
    result = await db['users'].update_one(
        {'email': email},
        {'$set': {'role': 'admin'}}
    )
    
    if result.modified_count > 0:
        print(f'✅ User {email} set to admin role')
    else:
        user = await db['users'].find_one({'email': email})
        if user:
            current_role = user.get('role', 'user')
            if current_role == 'admin':
                print(f'ℹ️  User {email} already has admin role')
            else:
                print(f'⚠️  Failed to update user {email}')
        else:
            print(f'❌ User {email} not found')
            print('\nAvailable users:')
            users = await db['users'].find({}).to_list(length=100)
            for u in users:
                print(f'  - {u.get("email")}: role={u.get("role", "user")}')
    
    client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python set_admin.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    asyncio.run(set_admin(email))
