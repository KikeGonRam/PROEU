import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.user_db import UserDB
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_count():
    db = AsyncIOMotorClient('mongodb://localhost:27017')['utvt_db']
    user_db = UserDB(db)
    async for doc in user_db.collection.find({"status": "active"}):
        print(doc)
    count = await user_db.count_documents()
    print(f"Total active users: {count}")

if __name__ == "__main__":
    asyncio.run(test_count())