"""호스팅 비즈니스 로직."""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.hosting.models import Hosting, HostingStatus
from app.domain.hosting.schemas import HostingCreateRequest, HostingResponse, HostingUpdateRequest
from app.domain.senior.models import Senior


async def get_guardian_senior_by_id(
    session: AsyncSession,
    guardian_id: int,
    senior_id: int,
) -> Senior:
    """보호자 소유의 어르신 엔티티를 조회합니다."""

    result = await session.execute(
        select(Senior).where(
            Senior.senior_id == senior_id,
            Senior.guardian_id == guardian_id,
        )
    )
    senior = result.scalar_one_or_none()

    if senior is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 보호자의 어르신 정보를 찾을 수 없습니다.",
        )

    return senior


async def get_guardian_hosting_by_id(
    session: AsyncSession,
    guardian_id: int,
    hosting_id: int,
) -> Hosting:
    """보호자 소유의 호스팅 엔티티를 조회합니다."""

    stmt = (
        select(Hosting)
        .join(Senior, Senior.senior_id == Hosting.senior_id)
        .where(
            Hosting.hosting_id == hosting_id,
            Senior.guardian_id == guardian_id,
        )
    )

    result = await session.execute(stmt)
    hosting = result.scalar_one_or_none()

    if hosting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 보호자의 호스팅 정보를 찾을 수 없습니다.",
        )

    return hosting


def get_now_utc() -> datetime:
    """현재 UTC 시간을 반환합니다."""

    return datetime.now(timezone.utc)


async def process_hosting_status_by_time(
    hosting: Hosting,
) -> bool:
    """호스팅 1건의 시간 기반 상태를 처리합니다."""

    now = get_now_utc()
    deadline_at = hosting.hosting_at - timedelta(hours=12)
    current_status = hosting.hosting_status
    new_status = current_status

    if now >= hosting.hosting_end:
        if current_status == HostingStatus.IN_PROGRESS:
            new_status = HostingStatus.CLOSED
        elif current_status != HostingStatus.CLOSED:
            new_status = HostingStatus.FAILED

    elif now >= deadline_at:
        if current_status not in {
            HostingStatus.FULL,
            HostingStatus.IN_PROGRESS,
            HostingStatus.CLOSED,
        }:
            new_status = HostingStatus.FAILED

    if new_status == current_status:
        return False

    hosting.hosting_status = new_status
    return True


async def run_hosting_status_scheduler(
    session: AsyncSession,
) -> int:
    """시간 조건이 도래한 호스팅 상태를 일괄 처리합니다."""

    stmt = select(Hosting).where(
        Hosting.hosting_status.in_(
            [
                HostingStatus.OPEN,
                HostingStatus.FULL,
                HostingStatus.IN_PROGRESS,
            ]
        )
    )

    result = await session.execute(stmt)
    hostings = result.scalars().all()

    changed_count = 0

    for hosting in hostings:
        is_changed = await process_hosting_status_by_time(
            hosting=hosting,
        )
        if is_changed:
            changed_count += 1

    if changed_count > 0:
        await session.commit()

    return changed_count


async def create_hosting(
    session: AsyncSession,
    guardian_id: int,
    request: HostingCreateRequest,
) -> HostingResponse:
    """호스팅을 등록합니다."""

    senior = await get_guardian_senior_by_id(
        session=session,
        guardian_id=guardian_id,
        senior_id=request.senior_id,
    )

    if not senior.active_flag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 어르신으로는 호스팅을 등록할 수 없습니다.",
        )

    hosting_max_people = request.max_people
    if hosting_max_people is None:
        hosting_max_people = senior.max_people

    hosting = Hosting(
        senior_id=senior.senior_id,
        menu=request.menu,
        hosting_at=request.hosting_at,
        hosting_end=request.hosting_end,
        max_people=hosting_max_people,
        hosting_status=HostingStatus.OPEN,
    )

    session.add(hosting)
    await session.commit()
    await session.refresh(hosting)

    return HostingResponse.model_validate(hosting)


async def list_hostings_by_guardian(
    session: AsyncSession,
    guardian_id: int,
) -> list[HostingResponse]:
    """보호자 기준 호스팅 목록을 조회합니다."""

    stmt = (
        select(Hosting)
        .join(Senior, Senior.senior_id == Hosting.senior_id)
        .where(Senior.guardian_id == guardian_id)
        .order_by(Hosting.created_at.desc())
    )

    result = await session.execute(stmt)
    hostings = result.scalars().all()

    return [HostingResponse.model_validate(hosting) for hosting in hostings]


async def get_hosting_detail(
    session: AsyncSession,
    guardian_id: int,
    hosting_id: int,
) -> HostingResponse:
    """보호자의 호스팅 상세 정보를 조회합니다."""

    hosting = await get_guardian_hosting_by_id(
        session=session,
        guardian_id=guardian_id,
        hosting_id=hosting_id,
    )

    return HostingResponse.model_validate(hosting)


async def cancel_hosting(
    session: AsyncSession,
    guardian_id: int,
    hosting_id: int,
) -> HostingResponse:
    """호스팅을 취소합니다."""

    hosting = await get_guardian_hosting_by_id(
        session=session,
        guardian_id=guardian_id,
        hosting_id=hosting_id,
    )

    if hosting.hosting_status in {HostingStatus.IN_PROGRESS, HostingStatus.CLOSED}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 진행 중이거나 완료된 호스팅은 무산 처리할 수 없습니다.",
        )

    hosting.hosting_status = HostingStatus.FAILED
    await session.commit()
    await session.refresh(hosting)

    return HostingResponse.model_validate(hosting)
