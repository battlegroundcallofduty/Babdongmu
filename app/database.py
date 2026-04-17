from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """DB 초기화.
    - SQLite + DB 없음: create_all로 최초 생성
    - SQLite + DB 있음 + DEBUG=True: alembic upgrade head로 스키마 변경 반영
    - PostgreSQL: deploy.yml에서 alembic upgrade head 담당
    """
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    import os
    # DATABASE_URL에서 파일 경로 추출 (sqlite+aiosqlite:///./babdongmu.db → ./babdongmu.db)
    db_path = settings.DATABASE_URL.split("///")[-1]
    db_exists = os.path.exists(db_path)

    if not db_exists:
        from app.domain.hosting.models import Hosting, SmsLog  # noqa: F401
        from app.domain.match.models import MatchingInfo  # noqa: F401
        from app.domain.review.models import Review, ReviewImg  # noqa: F401
        from app.domain.senior.models import Senior  # noqa: F401
        from app.domain.user.models import Document, User  # noqa: F401

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    elif settings.DEBUG:
        from alembic import command
        from alembic.config import Config
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")


async def close_db() -> None:
    """DB 연결을 종료합니다."""
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """DB 세션을 반환하는 의존성 함수입니다."""
    async with AsyncSessionLocal() as session:
        yield session
