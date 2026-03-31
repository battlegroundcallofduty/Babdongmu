"""AI 관련 API 엔드포인트."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/seniors/{senior_id}/summary")
async def generate_summary(senior_id: str):
    """어르신 AI 소개글을 수동 생성/갱신합니다 (관리자용)."""
    raise HTTPException(status_code=501, detail="미구현")


@router.get("/seniors/{senior_id}/summary")
async def get_summary(senior_id: str):
    """어르신 AI 소개글을 조회합니다."""
    raise HTTPException(status_code=501, detail="미구현")
