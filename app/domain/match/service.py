"""매칭 비즈니스 로직."""

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.hosting.models import Hosting
from app.domain.match.models import MatchingInfo


async def create_match(db: AsyncSession, hosting_id: int, vt_id: int) -> MatchingInfo:
    """매칭을 생성합니다."""

    # 1. 호스팅 존재 여부 확인
    hosting = await db.get(Hosting, hosting_id)
    if not hosting:
        raise HTTPException(status_code=404, detail="존재하지 않는 호스팅입니다.")

    # 2. 호스팅 상태 확인
    if hosting.hosting_status != "신청가능":
        raise HTTPException(status_code=400, detail="신청 불가능한 호스팅입니다.")

    # 3. 중복 신청 확인
    result = await db.execute(
        select(MatchingInfo).where(
            MatchingInfo.hosting_id == hosting_id,
            MatchingInfo.vt_id == vt_id,
            MatchingInfo.is_apply == True,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="이미 신청한 호스팅입니다.")

    # 4. 매칭 생성
    match = MatchingInfo(hosting_id=hosting_id, vt_id=vt_id)
    db.add(match)

    # 5. 정원 찼는지 확인 후 호스팅 상태 업데이트
    count_result = await db.execute(
        select(func.count()).where(
            MatchingInfo.hosting_id == hosting_id,
            MatchingInfo.is_apply == True,
        )
    )
    current_count = count_result.scalar()
    if current_count + 1 >= hosting.max_people:
        hosting.hosting_status = "모집완료"

    await db.commit()
    await db.refresh(match)
    return match


async def list_matches_by_volunteer(db: AsyncSession, vt_id: int) -> list[MatchingInfo]:
    """봉사자의 매칭 목록을 조회합니다."""
    result = await db.execute(
        select(MatchingInfo).where(MatchingInfo.vt_id == vt_id)
    )
    return result.scalars().all()


async def check(db: AsyncSession, senior_id: int, vt_id: int) -> MatchingInfo:
    """체크인 안 됐으면 체크인, 됐으면 체크아웃 갱신."""
    result = await db.execute(
        select(MatchingInfo).where(
            MatchingInfo.senior_id == senior_id,
            MatchingInfo.vt_id == vt_id,
            MatchingInfo.is_apply == True,
        )
    )
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(status_code=404, detail="존재하지 않는 매칭입니다.")

    if not match.check_in:
        match.check_in = True
        match.check_in_time = datetime.now(timezone.utc)
    else:
        match.check_out_time = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(match)
    return match