"""매칭 API 엔드포인트."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.match import service
from app.domain.match.schemas import MatchResponse
from app.domain.user.dependency import get_current_user
from app.domain.user.models import User

router = APIRouter()


def _require_volunteer(current_user: User) -> None:
    """봉사자 역할인지 확인합니다."""
    if current_user.user_role != "volunteer":
        raise HTTPException(status_code=403, detail="봉사자만 이용할 수 있습니다.")


@router.post("", response_model=MatchResponse)
async def create_match(
    hosting_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """호스팅에 매칭을 신청합니다."""
    _require_volunteer(current_user)
    return await service.create_match(db, hosting_id, current_user.user_id)


@router.get("/my", response_model=list[MatchResponse])
async def list_my_matches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """내 매칭 목록을 조회합니다."""
    _require_volunteer(current_user)
    return await service.list_matches_by_volunteer(db, current_user.user_id)


@router.patch("/{matching_id}/cancel", response_model=MatchResponse)
async def cancel_match(
    matching_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """매칭을 취소합니다."""
    _require_volunteer(current_user)
    return await service.cancel_match(db, matching_id, current_user.user_id)


@router.patch("/{senior_id}/check", response_model=MatchResponse)
async def check(
    senior_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """QR 체크인/아웃합니다."""
    _require_volunteer(current_user)
    return await service.check(db, senior_id, current_user.user_id)
