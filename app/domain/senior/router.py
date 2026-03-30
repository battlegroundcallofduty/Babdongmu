"""어르신 API 엔드포인트."""

from fastapi import APIRouter, HTTPException

from app.domain.senior.schema import SeniorCreateRequest, SeniorResponse

router = APIRouter()


@router.post("", response_model=SeniorResponse)
async def create_senior(request: SeniorCreateRequest) -> SeniorResponse:
    """어르신을 등록합니다 (보호자 대리)."""
    raise HTTPException(status_code=501, detail="미구현")


@router.get("", response_model=list[SeniorResponse])
async def list_seniors(district: str | None = None) -> list[SeniorResponse]:
    """어르신 목록을 조회합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.get("/{senior_id}", response_model=SeniorResponse)
async def get_senior(senior_id: str) -> SeniorResponse:
    """어르신 상세 정보를 조회합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.put("/{senior_id}", response_model=SeniorResponse)
async def update_senior(senior_id: str, request: SeniorCreateRequest) -> SeniorResponse:
    """어르신 정보를 수정합니다."""
    raise HTTPException(status_code=501, detail="미구현")
