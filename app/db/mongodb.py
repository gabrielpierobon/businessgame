"""
MongoDB connector for the Business Game.
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "business_game")

# MongoDB client instance
client = None
db = None

async def connect_to_mongo():
    """
    Connect to MongoDB.
    """
    global client, db
    
    # Create MongoDB client
    client = AsyncIOMotorClient(MONGO_URL)
    
    # Get database
    db = client[MONGO_DB_NAME]
    
    print(f"Connected to MongoDB at {MONGO_URL}, database: {MONGO_DB_NAME}")

async def close_mongo_connection():
    """
    Close MongoDB connection.
    """
    global client
    
    if client:
        client.close()
        print("Closed MongoDB connection")

def get_db():
    """
    Get MongoDB database instance.
    """
    return db 