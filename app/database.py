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
    """DB 초기화.
    - SQLite + DB 없음: create_all로 최초 생성 후 alembic stamp head로 버전 기록
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
        import asyncio

        import app.domain  # noqa: F401 — 모든 모델을 Base.metadata에 등록
        from alembic import command
        from alembic.config import Config

        # 테이블 생성
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # create_all은 SQL만 실행하고 alembic_version을 남기지 않음.
        # 다음 기동 때 upgrade head가 001을 재실행하려다 충돌하는 걸 막기 위해
        # "지금 DB가 최신 revision 상태"임을 alembic에 기록만 해둠.
        alembic_cfg = Config("alembic.ini")
        await asyncio.to_thread(command.stamp, alembic_cfg, "head")
    elif settings.DEBUG:
        import asyncio

        from alembic import command
        from alembic.config import Config
        alembic_cfg = Config("alembic.ini")
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")


async def close_db() -> None:
    """DB 연결을 종료합니다."""
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """DB 세션을 반환하는 의존성 함수입니다."""
    async with AsyncSessionLocal() as session:
        yield session
