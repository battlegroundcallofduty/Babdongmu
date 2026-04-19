from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.database import close_db, init_db
from app.scheduler import hosting_scheduler_loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 DB와 스케줄러를 관리합니다."""

    # 1. DB 초기화
    await init_db()

    # 2. 스케줄러 시작
    scheduler_task = asyncio.create_task(hosting_scheduler_loop())

    try:
        yield

    finally:
        # 3. 스케줄러 종료
        scheduler_task.cancel()

        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass

        # 4. DB 종료
        await close_db()


app = FastAPI(
    title="밥동무 API",
    description="독거 어르신을 위한 식사 동반 플랫폼",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
