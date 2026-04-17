from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)

# SQLite는 외래키 CASCADE가 기본 비활성화 → 로컬 테스트용으로 활성화
# PostgreSQL(배포)은 자동 적용이라 해당 없음
if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """데이터베이스 테이블을 생성합니다."""
    # 모든 모델을 import해야 Base.metadata에 등록됩니다
    from app.domain.hosting.models import Hosting, SmsLog  # noqa: F401
    from app.domain.match.models import MatchingInfo  # noqa: F401
    from app.domain.review.models import Review, ReviewImg  # noqa: F401
    from app.domain.senior.models import Senior  # noqa: F401
    from app.domain.user.models import Document, User  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """DB 연결을 종료합니다."""
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """DB 세션을 반환하는 의존성 함수입니다."""
    async with AsyncSessionLocal() as session:
        yield session
