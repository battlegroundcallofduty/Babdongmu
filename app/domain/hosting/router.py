"""호스팅 API 엔드포인트."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("")
async def create_hosting():
    """호스팅을 신청합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.get("")
async def list_hostings(district: str | None = None, status: str | None = None):
    """호스팅 목록을 조회합니다 (동네/상태 필터)."""
    raise HTTPException(status_code=501, detail="미구현")


@router.get("/{hosting_id}")
async def get_hosting(hosting_id: str):
    """호스팅 상세 정보를 조회합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.patch("/{hosting_id}/approve")
async def approve_hosting(hosting_id: str):
    """호스팅을 승인합니다 (관리자 전용)."""
    raise HTTPException(status_code=501, detail="미구현")
