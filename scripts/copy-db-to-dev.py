#!/usr/bin/env python3
"""
Copy database from production (german_ai) to development (german_ai_dev)
This creates a snapshot of production data for safe development testing.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def copy_database():
    """Copy all collections from german_ai to german_ai_dev"""
    
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("❌ Error: MONGODB_URI not set in environment")
        return
    
    print("🔄 Copying database: german_ai → german_ai_dev")
    print("=" * 60)
    
    client = AsyncIOMotorClient(mongodb_uri)
    
    source_db = client["german_ai"]
    target_db = client["german_ai_dev"]
    
    # Get all collections from source
    collections = await source_db.list_collection_names()
    print(f"\nFound {len(collections)} collections to copy:")
    for col in collections:
        print(f"  - {col}")
    
    print("\n" + "=" * 60)
    
    total_docs = 0
    
    for collection_name in collections:
        print(f"\n📦 Copying collection: {collection_name}")
        
        source_col = source_db[collection_name]
        target_col = target_db[collection_name]
        
        # Drop existing collection in target
        await target_col.drop()
        
        # Copy all documents
        documents = await source_col.find({}).to_list(length=10000)
        
        if documents:
            await target_col.insert_many(documents)
            print(f"   ✅ Copied {len(documents)} documents")
            total_docs += len(documents)
        else:
            print(f"   ⚠️  No documents found")
        
        # Copy indexes
        indexes = await source_col.list_indexes().to_list(length=100)
        for index in indexes:
            if index['name'] != '_id_':  # Skip default _id index
                try:
                    keys = index['key']
                    options = {k: v for k, v in index.items() if k not in ['key', 'v', 'ns']}
                    await target_col.create_index(list(keys.items()), **options)
                    print(f"   📑 Created index: {index['name']}")
                except Exception as e:
                    print(f"   ⚠️  Could not create index {index['name']}: {e}")
    
    print("\n" + "=" * 60)
    print(f"\n✅ Database copy complete!")
    print(f"   Total documents copied: {total_docs}")
    print(f"   Source: german_ai")
    print(f"   Target: german_ai_dev")
    print(f"   Timestamp: {datetime.utcnow().isoformat()}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(copy_database())
