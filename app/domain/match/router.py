"""매칭 API 엔드포인트."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.user.dependency import get_current_user
from app.domain.match import service
from app.domain.user.models import User

router = APIRouter()


@router.post("")
async def create_match(
    hosting_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """호스팅에 매칭을 신청합니다."""
    return await service.create_match(db, hosting_id, current_user.user_id)


@router.get("/my")
async def list_my_matches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """내 매칭 목록을 조회합니다."""
    return await service.list_matches_by_volunteer(db, current_user.user_id)


@router.patch("/{match_id}/checkin")
async def checkin(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """체크인합니다."""
    return await service.checkin(db, match_id, current_user.user_id)


@router.patch("/{match_id}/checkout")
async def checkout(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """체크아웃합니다. 봉사시간이 자동 계산됩니다."""
    return await service.checkout(db, match_id, current_user.user_id)