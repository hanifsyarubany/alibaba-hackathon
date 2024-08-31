from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO_DB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "mydatabase"

settings = Settings()

client = AsyncIOMotorClient(settings.MONGO_DB_URL)
database = client[settings.DATABASE_NAME]
