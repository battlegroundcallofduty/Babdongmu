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


@router.patch("/{senior_id}/check")
async def check(
    senior_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """QR 체크인/아웃합니다."""
    return await service.check(db, senior_id, current_user.user_id)