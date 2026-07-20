"""Async MongoDB connection management via Motor."""

from collections.abc import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


async def get_database() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """FastAPI dependency that yields the Motor database instance."""
    if db is None:
        raise RuntimeError("MongoDB is not connected. Call connect_db() first.")
    yield db


async def connect_db() -> None:
    """Create the Motor client and select the database."""
    global client, db
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]


async def close_db() -> None:
    """Close the Motor client connection."""
    global client
    if client is not None:
        client.close()
        client = None
