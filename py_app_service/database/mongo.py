from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pydantic import BaseModel
from ..config import MONGODB_URI, MONGODB_NAME

class Settings(BaseModel):
    MONGO_DB_URL: str
    DATABASE_NAME: str

settings = Settings(MONGO_DB_URL=MONGODB_URI, DATABASE_NAME=MONGODB_NAME)

client = AsyncIOMotorClient(settings.MONGO_DB_URL)
database = client[settings.DATABASE_NAME]
