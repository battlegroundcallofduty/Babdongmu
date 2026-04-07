from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """데이터베이스 테이블을 생성합니다."""
    # 모든 모델을 import해야 Base.metadata에 등록됩니다
    from app.domain.user.models import User, Document  # noqa: F401
    from app.domain.senior.models import Senior  # noqa: F401
    from app.domain.hosting.models import Hosting, SmsLog  # noqa: F401
    from app.domain.match.models import MatchingInfo  # noqa: F401
    from app.domain.review.models import Review, ReviewImg  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """DB 연결을 종료합니다."""
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """DB 세션을 반환하는 의존성 함수입니다."""
    async with AsyncSessionLocal() as session:
        yield session
