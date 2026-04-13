"""매칭 비즈니스 로직."""

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.hosting.models import Hosting, HostingStatus
from app.domain.match.models import MatchingInfo, MatchStatus


async def create_match(db: AsyncSession, hosting_id: int, vt_id: int) -> MatchingInfo:
    """매칭을 생성합니다."""

    # 1. 호스팅 존재 여부 확인
    hosting = await db.get(Hosting, hosting_id)
    if not hosting:
        raise HTTPException(status_code=404, detail="존재하지 않는 호스팅입니다.")

    # 2. 호스팅 상태 확인
    if hosting.hosting_status != HostingStatus.OPEN:
        raise HTTPException(status_code=400, detail="신청 불가능한 호스팅입니다.")

    # 3. 중복 신청 확인
    result = await db.execute(
        select(MatchingInfo).where(
            MatchingInfo.hosting_id == hosting_id,
            MatchingInfo.vt_id == vt_id,
            MatchingInfo.match_status != MatchStatus.CANCELLED,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="이미 신청한 호스팅입니다.")

    # 4. 선착순 매칭 생성 (즉시 승인)
    match = MatchingInfo(
        hosting_id=hosting_id,
        vt_id=vt_id,
        senior_id=hosting.senior_id,
        match_status=MatchStatus.APPROVED,
    )
    db.add(match)
    await db.flush()

    # 5. 승인 인원이 max_people에 도달하면 모집완료로 변경
    count_result = await db.execute(
        select(func.count()).where(
            MatchingInfo.hosting_id == hosting_id,
            MatchingInfo.match_status == MatchStatus.APPROVED,
        )
    )
    if count_result.scalar() >= hosting.max_people:
        hosting.hosting_status = HostingStatus.FULL

    await db.commit()
    await db.refresh(match)
    return match


async def list_matches_by_volunteer(db: AsyncSession, vt_id: int) -> list[MatchingInfo]:
    """봉사자의 매칭 목록을 조회합니다."""
    result = await db.execute(
        select(MatchingInfo).where(
            MatchingInfo.vt_id == vt_id,
            MatchingInfo.match_status != MatchStatus.CANCELLED,
        )
    )
    return result.scalars().all()


async def cancel_match(db: AsyncSession, matching_id: int, vt_id: int) -> MatchingInfo:
    """매칭을 취소합니다."""
    match = await db.get(MatchingInfo, matching_id)

    if not match:
        raise HTTPException(status_code=404, detail="존재하지 않는 매칭입니다.")

    # 본인 매칭인지 확인
    if match.vt_id != vt_id:
        raise HTTPException(status_code=403, detail="본인 매칭만 취소할 수 있습니다.")

    # 이미 취소된 매칭 방어
    if match.match_status == MatchStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="이미 취소된 매칭입니다.")

    match.match_status = MatchStatus.CANCELLED
    await db.flush()

    # 취소 후 승인 인원이 줄었으면 호스팅 다시 신청가능으로 복구
    hosting = await db.get(Hosting, match.hosting_id)
    if hosting and hosting.hosting_status == HostingStatus.FULL:
        count_result = await db.execute(
            select(func.count()).where(
                MatchingInfo.hosting_id == match.hosting_id,
                MatchingInfo.match_status == MatchStatus.APPROVED,
            )
        )
        if count_result.scalar() < hosting.max_people:
            hosting.hosting_status = HostingStatus.OPEN

    await db.commit()
    await db.refresh(match)
    return match


async def check(db: AsyncSession, senior_id: int, vt_id: int) -> MatchingInfo:
    """체크인 안 됐으면 체크인, 됐으면 체크아웃 갱신."""
    result = await db.execute(
        select(MatchingInfo).where(
            MatchingInfo.senior_id == senior_id,
            MatchingInfo.vt_id == vt_id,
            MatchingInfo.match_status == MatchStatus.APPROVED,
        )
    )
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(status_code=404, detail="존재하지 않는 매칭입니다.")

    # 체크아웃 완료된 매칭 재요청 방어
    if match.check_out_time:
        raise HTTPException(status_code=400, detail="이미 체크아웃 완료된 매칭입니다.")

    if not match.check_in_time:
        match.check_in_time = datetime.now(timezone.utc)
    else:
        match.check_out_time = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(match)
    return match
