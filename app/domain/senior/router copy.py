"""어르신 API 엔드포인트."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("")
async def create_senior():
    """어르신을 등록합니다 (보호자 대리)."""
    raise HTTPException(status_code=501, detail="미구현")


@router.get("")
async def list_seniors(district: str | None = None):
    """어르신 목록을 조회합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.get("/{senior_id}")
async def get_senior(senior_id: str):
    """어르신 상세 정보를 조회합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.put("/{senior_id}")
async def update_senior(senior_id: str):
    """어르신 정보를 수정합니다."""
    raise HTTPException(status_code=501, detail="미구현")
