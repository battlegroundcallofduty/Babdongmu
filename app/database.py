from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

client: AsyncIOMotorClient | None = None
db = None


async def connect_db() -> None:
    """MongoDB에 연결합니다."""
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.MONGO_DB]


async def close_db() -> None:
    """MongoDB 연결을 종료합니다."""
    global client
    if client:
        client.close()


def get_db():
    """현재 DB 인스턴스를 반환합니다."""
    return db
