"""호스팅 비즈니스 로직."""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.hosting.models import Hosting, HostingStatus
from app.domain.hosting.schema import HostingCreateRequest, HostingResponse, HostingUpdateRequest
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


async def get_approved_match_count(
    session: AsyncSession,
    hosting_id: int,
) -> int:
    """호스팅의 승인된 매칭 인원 수를 조회합니다.

    TODO:
    match 도메인 모델이 연결되면 실제 승인된 매칭 수를 조회하도록 수정합니다.
    현재는 hosting_status 재계산 구조만 먼저 잡아둔 상태입니다.
    """

    _ = session
    _ = hosting_id
    return 0


async def has_check_in(
    session: AsyncSession,
    hosting_id: int,
) -> bool:
    """호스팅의 체크인 발생 여부를 조회합니다.

    TODO:
    match 도메인 모델이 연결되면 check_in_time 존재 여부를 조회하도록 수정합니다.
    """

    _ = session
    _ = hosting_id
    return False


async def has_completed_check_out(
    session: AsyncSession,
    hosting_id: int,
) -> bool:
    """호스팅의 정상 체크아웃 완료 여부를 조회합니다.

    TODO:
    match 도메인 모델이 연결되면 check_out_time 존재 여부를 조회하도록 수정합니다.
    """

    _ = session
    _ = hosting_id
    return False


def get_now_utc() -> datetime:
    """현재 UTC 시간을 반환합니다."""

    return datetime.now(timezone.utc)


async def recalculate_hosting_status(
    session: AsyncSession,
    hosting: Hosting,
) -> HostingStatus:
    """호스팅 상태를 현재 시점 기준으로 재계산합니다."""

    now = get_now_utc()
    approved_match_count = await get_approved_match_count(session=session, hosting_id=hosting.hosting_id)
    checked_in = await has_check_in(session=session, hosting_id=hosting.hosting_id)
    checked_out = await has_completed_check_out(session=session, hosting_id=hosting.hosting_id)

    if checked_out or now >= hosting.hosting_end:
        return HostingStatus.CLOSED

    if checked_in:
        return HostingStatus.IN_PROGRESS

    deadline_at = hosting.hosting_at - timedelta(hours=12)

    if now >= deadline_at and approved_match_count < hosting.max_people:
        return HostingStatus.FAILED

    if approved_match_count >= hosting.max_people:
        return HostingStatus.FULL

    return HostingStatus.OPEN


async def sync_hosting_status(
    session: AsyncSession,
    hosting: Hosting,
) -> Hosting:
    """호스팅 상태를 재계산 후 DB에 반영합니다."""

    new_status = await recalculate_hosting_status(session=session, hosting=hosting)

    if hosting.hosting_status != new_status:
        hosting.hosting_status = new_status
        await session.commit()
        await session.refresh(hosting)

    return hosting


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

    hosting = await sync_hosting_status(session=session, hosting=hosting)
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

    responses: list[HostingResponse] = []
    for hosting in hostings:
        hosting = await sync_hosting_status(session=session, hosting=hosting)
        responses.append(HostingResponse.model_validate(hosting))

    return responses


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
    hosting = await sync_hosting_status(session=session, hosting=hosting)

    return HostingResponse.model_validate(hosting)


async def update_hosting(
    session: AsyncSession,
    guardian_id: int,
    hosting_id: int,
    request: HostingUpdateRequest,
) -> HostingResponse:
    """호스팅 정보를 수정합니다."""

    hosting = await get_guardian_hosting_by_id(
        session=session,
        guardian_id=guardian_id,
        hosting_id=hosting_id,
    )

    if hosting.hosting_status in {HostingStatus.IN_PROGRESS, HostingStatus.CLOSED, HostingStatus.FAILED}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="진행 중이거나 종료된 호스팅은 수정할 수 없습니다.",
        )

    update_data = request.model_dump(exclude_unset=True)

    for field_name, field_value in update_data.items():
        setattr(hosting, field_name, field_value)

    await session.commit()
    await session.refresh(hosting)

    hosting = await sync_hosting_status(session=session, hosting=hosting)
    return HostingResponse.model_validate(hosting)


async def fail_hosting(
    session: AsyncSession,
    guardian_id: int,
    hosting_id: int,
) -> HostingResponse:
    """호스팅을 취소 또는 무산 상태로 변경합니다."""

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


async def mark_hosting_in_progress(
    session: AsyncSession,
    hosting_id: int,
) -> Hosting:
    """호스팅을 진행 중 상태로 변경합니다.

    TODO:
    실제 check-in 로직에서 호출하도록 연결합니다.
    """

    result = await session.execute(select(Hosting).where(Hosting.hosting_id == hosting_id))
    hosting = result.scalar_one_or_none()

    if hosting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="호스팅 정보를 찾을 수 없습니다.",
        )

    if hosting.hosting_status not in {HostingStatus.FULL, HostingStatus.OPEN}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 상태에서는 진행 시작 처리할 수 없습니다.",
        )

    hosting.hosting_status = HostingStatus.IN_PROGRESS
    await session.commit()
    await session.refresh(hosting)

    return hosting


async def mark_hosting_closed(
    session: AsyncSession,
    hosting_id: int,
) -> Hosting:
    """호스팅을 완료 상태로 변경합니다.

    TODO:
    실제 check-out 로직에서 호출하도록 연결합니다.
    """

    result = await session.execute(select(Hosting).where(Hosting.hosting_id == hosting_id))
    hosting = result.scalar_one_or_none()

    if hosting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="호스팅 정보를 찾을 수 없습니다.",
        )

    if hosting.hosting_status != HostingStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="진행 중인 호스팅만 완료 처리할 수 있습니다.",
        )

    hosting.hosting_status = HostingStatus.CLOSED
    await session.commit()
    await session.refresh(hosting)

    return hosting


async def delete_hosting(
    session: AsyncSession,
    guardian_id: int,
    hosting_id: int,
) -> None:
    """호스팅을 삭제합니다."""

    hosting = await get_guardian_hosting_by_id(
        session=session,
        guardian_id=guardian_id,
        hosting_id=hosting_id,
    )

    if hosting.hosting_status == HostingStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="진행 중인 호스팅은 삭제할 수 없습니다.",
        )

    await session.delete(hosting)
    await session.commit()