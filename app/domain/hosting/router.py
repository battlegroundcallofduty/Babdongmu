"""호스팅 API 엔드포인트."""

from fastapi import APIRouter, HTTPException

from app.domain.hosting.schema import HostingCreateRequest, HostingResponse

router = APIRouter()


@router.post("", response_model=HostingResponse)
async def create_hosting(request: HostingCreateRequest) -> HostingResponse:
    """호스팅을 신청합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.get("", response_model=list[HostingResponse])
async def list_hostings(
    district: str | None = None,
    status: str | None = None,
) -> list[HostingResponse]:
    """호스팅 목록을 조회합니다 (동네/상태 필터)."""
    raise HTTPException(status_code=501, detail="미구현")


@router.get("/{hosting_id}", response_model=HostingResponse)
async def get_hosting(hosting_id: str) -> HostingResponse:
    """호스팅 상세 정보를 조회합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.patch("/{hosting_id}/approve")
async def approve_hosting(hosting_id: str) -> dict:
    """호스팅을 승인합니다 (관리자 전용)."""
    raise HTTPException(status_code=501, detail="미구현")
