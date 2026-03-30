"""매칭 API 엔드포인트."""

from fastapi import APIRouter, HTTPException

from app.domain.match.schema import MatchCreateRequest, MatchResponse

router = APIRouter()


@router.post("", response_model=MatchResponse)
async def create_match(request: MatchCreateRequest) -> MatchResponse:
    """호스팅에 매칭을 신청합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.get("/my", response_model=list[MatchResponse])
async def list_my_matches(status: str | None = None) -> list[MatchResponse]:
    """내 매칭 목록을 조회합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.patch("/{match_id}/checkin")
async def checkin(match_id: str) -> dict:
    """체크인합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.patch("/{match_id}/checkout")
async def checkout(match_id: str) -> dict:
    """체크아웃합니다. 봉사시간이 자동 계산됩니다."""
    raise HTTPException(status_code=501, detail="미구현")
