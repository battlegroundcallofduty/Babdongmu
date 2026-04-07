from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 DB 연결을 관리합니다."""
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="밥동무 API",
    description="독거 어르신을 위한 식사 동반 플랫폼",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
