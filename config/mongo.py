from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

# Initialize MongoDB connection
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

# Collections
documents_collection = db["documents"]