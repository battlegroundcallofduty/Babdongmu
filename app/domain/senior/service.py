"""어르신 CRUD 로직."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.hosting.models import Hosting, HostingStatus
from app.domain.senior.models import Senior
from app.domain.senior.schemas import (
    SeniorCreateRequest,
    SeniorResponse,
    SeniorUpdateRequest,
    calculate_age_from_birth_date,
)

HostingCountMap = dict[str, int]

BLOCKING_HOSTING_STATUSES_FOR_DEACTIVATION = (
    HostingStatus.OPEN,
    HostingStatus.FULL,
    HostingStatus.FIXED,
    HostingStatus.IN_PROGRESS,
)


def build_senior_response(
    senior: Senior,
    hosting_counts: HostingCountMap | None = None,
) -> SeniorResponse:
    """어르신 응답 데이터를 생성합니다."""

    counts = hosting_counts or {}

    return SeniorResponse(
        senior_id=senior.senior_id,
        guardian_id=senior.guardian_id,
        name=senior.name,
        gender=senior.gender,
        birth_date=senior.birth_date,
        age=calculate_age_from_birth_date(senior.birth_date),
        road_address=senior.road_address,
        jibun_address=senior.jibun_address,
        zonecode=senior.zonecode,
        sigungu=senior.sigungu,
        bname=senior.bname,
        detail_address=senior.detail_address,
        sido=senior.sido,
        building_name=senior.building_name,
        is_apartment=senior.is_apartment,
        lat=senior.lat,
        lng=senior.lng,
        sigungu_code=senior.sigungu_code,
        special_note=senior.special_note,
        active_flag=senior.active_flag,
        ai_summary=senior.ai_summary,
        max_people=senior.max_people,
        qr_code=senior.qr_code,
        total_hosting_count=counts.get("total", 0),
        open_hosting_count=counts.get("open", 0),
        full_hosting_count=counts.get("full", 0),
        fixed_hosting_count=counts.get("fixed", 0),
        in_progress_hosting_count=counts.get("in_progress", 0),
        closed_hosting_count=counts.get("closed", 0),
        failed_hosting_count=counts.get("failed", 0),
        created_at=senior.created_at,
        updated_at=senior.updated_at,
    )


async def get_hosting_counts_by_senior(
    session: AsyncSession,
    senior_id: int,
) -> HostingCountMap:
    """어르신 1명의 호스팅 상태별 집계값을 조회합니다."""

    stmt = select(
        func.count(Hosting.hosting_id).label("total_hosting_count"),
        func.count(Hosting.hosting_id)
        .filter(Hosting.hosting_status == HostingStatus.OPEN)
        .label("open_hosting_count"),
        func.count(Hosting.hosting_id)
        .filter(Hosting.hosting_status == HostingStatus.FULL)
        .label("full_hosting_count"),
        func.count(Hosting.hosting_id)
        .filter(Hosting.hosting_status == HostingStatus.FIXED)
        .label("fixed_hosting_count"),
        func.count(Hosting.hosting_id)
        .filter(Hosting.hosting_status == HostingStatus.IN_PROGRESS)
        .label("in_progress_hosting_count"),
        func.count(Hosting.hosting_id)
        .filter(Hosting.hosting_status == HostingStatus.CLOSED)
        .label("closed_hosting_count"),
        func.count(Hosting.hosting_id)
        .filter(Hosting.hosting_status == HostingStatus.FAILED)
        .label("failed_hosting_count"),
    ).where(Hosting.senior_id == senior_id)

    result = await session.execute(stmt)
    row = result.one()

    return {
        "total": row.total_hosting_count or 0,
        "open": row.open_hosting_count or 0,
        "full": row.full_hosting_count or 0,
        "fixed": row.fixed_hosting_count or 0,
        "in_progress": row.in_progress_hosting_count or 0,
        "closed": row.closed_hosting_count or 0,
        "failed": row.failed_hosting_count or 0,
    }


async def ensure_senior_can_be_deactivated(
    session: AsyncSession,
    senior_id: int,
) -> None:
    """완료되지 않은 호스팅이 있으면 어르신 비활성화를 막습니다."""

    stmt = select(Hosting.hosting_id).where(
        Hosting.senior_id == senior_id,
        Hosting.hosting_status.in_(BLOCKING_HOSTING_STATUSES_FOR_DEACTIVATION),
    )

    result = await session.execute(stmt)
    hosting_id = result.scalar_one_or_none()

    if hosting_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="완료되지 않은 호스팅이 있는 어르신은 비활성화할 수 없습니다.",
        )


async def create_senior(
    session: AsyncSession,
    guardian_id: int,
    request: SeniorCreateRequest,
) -> SeniorResponse:
    """어르신을 등록합니다."""

    senior = Senior(
        guardian_id=guardian_id,
        name=request.name,
        gender=request.gender,
        birth_date=request.birth_date,
        road_address=request.road_address,
        jibun_address=request.jibun_address,
        zonecode=request.zonecode,
        sigungu=request.sigungu,
        bname=request.bname,
        detail_address=request.detail_address,
        sido=request.sido,
        building_name=request.building_name,
        is_apartment=request.is_apartment,
        lat=float(request.lat) if request.lat is not None else None,
        lng=float(request.lng) if request.lng is not None else None,
        sigungu_code=request.sigungu_code,
        special_note=request.special_note,
        active_flag=request.active_flag,
        max_people=request.max_people,
        qr_code=str(uuid.uuid4()),
    )

    session.add(senior)
    await session.commit()
    await session.refresh(senior)

    hosting_counts = await get_hosting_counts_by_senior(
        session=session,
        senior_id=senior.senior_id,
    )

    return build_senior_response(
        senior=senior,
        hosting_counts=hosting_counts,
    )


async def list_seniors_by_guardian(
    session: AsyncSession,
    guardian_id: int,
    active_only: bool = True,
) -> list[SeniorResponse]:
    """보호자 기준 어르신 목록을 조회합니다."""

    stmt = (
        select(
            Senior,
            func.count(Hosting.hosting_id).label("total_hosting_count"),
            func.count(Hosting.hosting_id)
            .filter(Hosting.hosting_status == HostingStatus.OPEN)
            .label("open_hosting_count"),
            func.count(Hosting.hosting_id)
            .filter(Hosting.hosting_status == HostingStatus.FULL)
            .label("full_hosting_count"),
            func.count(Hosting.hosting_id)
            .filter(Hosting.hosting_status == HostingStatus.FIXED)
            .label("fixed_hosting_count"),
            func.count(Hosting.hosting_id)
            .filter(Hosting.hosting_status == HostingStatus.IN_PROGRESS)
            .label("in_progress_hosting_count"),
            func.count(Hosting.hosting_id)
            .filter(Hosting.hosting_status == HostingStatus.CLOSED)
            .label("closed_hosting_count"),
            func.count(Hosting.hosting_id)
            .filter(Hosting.hosting_status == HostingStatus.FAILED)
            .label("failed_hosting_count"),
        )
        .outerjoin(Hosting, Hosting.senior_id == Senior.senior_id)
        .where(Senior.guardian_id == guardian_id)
    )

    if active_only:
        stmt = stmt.where(Senior.active_flag.is_(True))

    stmt = stmt.group_by(Senior.senior_id).order_by(Senior.created_at.desc())

    result = await session.execute(stmt)
    rows = result.all()

    return [
        build_senior_response(
            senior=senior,
            hosting_counts={
                "total": total_hosting_count or 0,
                "open": open_hosting_count or 0,
                "full": full_hosting_count or 0,
                "fixed": fixed_hosting_count or 0,
                "in_progress": in_progress_hosting_count or 0,
                "closed": closed_hosting_count or 0,
                "failed": failed_hosting_count or 0,
            },
        )
        for (
            senior,
            total_hosting_count,
            open_hosting_count,
            full_hosting_count,
            fixed_hosting_count,
            in_progress_hosting_count,
            closed_hosting_count,
            failed_hosting_count,
        ) in rows
    ]


async def get_senior_by_id(
    session: AsyncSession,
    senior_id: int,
) -> SeniorResponse:
    """ID로 어르신을 조회합니다."""

    result = await session.execute(
        select(Senior).where(Senior.senior_id == senior_id)
    )
    senior = result.scalar_one_or_none()

    if senior is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="어르신 정보를 찾을 수 없습니다.",
        )

    hosting_counts = await get_hosting_counts_by_senior(
        session=session,
        senior_id=senior.senior_id,
    )

    return build_senior_response(
        senior=senior,
        hosting_counts=hosting_counts,
    )


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


async def update_senior(
    session: AsyncSession,
    guardian_id: int,
    senior_id: int,
    request: SeniorUpdateRequest,
) -> SeniorResponse:
    """어르신 정보를 수정합니다."""

    senior = await get_guardian_senior_by_id(
        session=session,
        guardian_id=guardian_id,
        senior_id=senior_id,
    )

    update_data = request.model_dump(
        exclude_unset=True,
    )

    if update_data.get("active_flag") is False:
        await ensure_senior_can_be_deactivated(
            session=session,
            senior_id=senior.senior_id,
        )

    for field_name, field_value in update_data.items():
        setattr(senior, field_name, field_value)

    await session.commit()
    await session.refresh(senior)

    hosting_counts = await get_hosting_counts_by_senior(
        session=session,
        senior_id=senior.senior_id,
    )

    return build_senior_response(
        senior=senior,
        hosting_counts=hosting_counts,
    )


async def deactivate_senior(
    session: AsyncSession,
    guardian_id: int,
    senior_id: int,
) -> None:
    """어르신 정보를 비활성화합니다."""

    senior = await get_guardian_senior_by_id(
        session=session,
        guardian_id=guardian_id,
        senior_id=senior_id,
    )

    await ensure_senior_can_be_deactivated(
        session=session,
        senior_id=senior.senior_id,
    )

    senior.active_flag = False
    await session.commit()


async def activate_senior(
    session: AsyncSession,
    guardian_id: int,
    senior_id: int,
) -> None:
    """어르신 정보를 활성화합니다."""

    senior = await get_guardian_senior_by_id(
        session=session,
        guardian_id=guardian_id,
        senior_id=senior_id,
    )

    senior.active_flag = True
    await session.commit()


async def delete_senior(
    session: AsyncSession,
    guardian_id: int,
    senior_id: int,
) -> None:
    """어르신 정보를 삭제합니다."""

    senior = await get_guardian_senior_by_id(
        session=session,
        guardian_id=guardian_id,
        senior_id=senior_id,
    )

    await session.delete(senior)
    await session.commit()


async def get_senior_id_by_qr(
    session: AsyncSession,
    qr_uuid: str,
) -> int:
    """QR UUID로 senior_id를 역조회합니다."""

    result = await session.execute(
        select(Senior.senior_id).where(Senior.qr_code == qr_uuid)
    )
    senior_id = result.scalar_one_or_none()

    if senior_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유효하지 않은 QR 코드입니다.",
        )

    return senior_id
