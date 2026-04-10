
from motor.motor_asyncio import AsyncIOMotorClient
from src.config import settings

_mongo_client: AsyncIOMotorClient | None = None



async def get_db():
    global _mongo_client
    if _mongo_client is None:
        mongo_uri = settings.MONGODB_URI or settings.DATABASE_URL
        _mongo_client = AsyncIOMotorClient(mongo_uri)
    return _mongo_client["agro-link"]


async def get_sessions_collection(db):
    coll = db["sessions"]
    await coll.create_index("expiresAt", expireAfterSeconds=0)
    return coll





def close_connections():
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None

