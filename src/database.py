
from motor.motor_asyncio import AsyncIOMotorClient
from src.config import settings

_mongo_client: AsyncIOMotorClient | None = None



async def get_db():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)
    return _mongo_client["agro-link"]


async def get_sessions_collection(db):
    coll = db["sessions"]
    await coll.create_index("expiresAt", expireAfterSeconds=0)
    return coll





async def close_connections():
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()

