import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.database import close_db, init_db
from app.scheduler import hosting_scheduler_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)


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

logger = logging.getLogger(__name__)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """예상치 못한 500 에러를 로깅합니다."""
    logger.exception("Unhandled error: %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "서버 오류가 발생했습니다."})


app.include_router(api_router, prefix="/api/v1")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
