"""어르신 CRUD 로직."""

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.hosting.models import Hosting, HostingStatus
from app.domain.senior.models import Senior
from app.domain.senior.schemas import (
    SeniorCreateRequest,
    SeniorResponse,
    SeniorUpdateRequest,
)


async def build_senior_response(
    session: AsyncSession,
    senior: Senior,
) -> SeniorResponse:
    """어르신 응답 데이터를 생성합니다."""

    total_count_stmt = select(func.count(Hosting.hosting_id)).where(
        Hosting.senior_id == senior.senior_id,
    )
    total_count_result = await session.execute(total_count_stmt)
    total_hosting_count = total_count_result.scalar_one()

    full_count_stmt = select(func.count(Hosting.hosting_id)).where(
        Hosting.senior_id == senior.senior_id,
        Hosting.hosting_status == HostingStatus.FULL,
    )
    full_count_result = await session.execute(full_count_stmt)
    full_hosting_count = full_count_result.scalar_one()

    return SeniorResponse(
        senior_id=senior.senior_id,
        guardian_id=senior.guardian_id,
        name=senior.name,
        gender=senior.gender,
        age=senior.age,
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
        full_hosting_count=full_hosting_count,
        total_hosting_count=total_hosting_count,
        created_at=senior.created_at,
        updated_at=senior.updated_at,
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
        age=request.age,
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
    )

    session.add(senior)
    await session.commit()
    await session.refresh(senior)

    return await build_senior_response(
        session=session,
        senior=senior,
    )


async def list_seniors_by_guardian(
    session: AsyncSession,
    guardian_id: int,
    active_only: bool = True,
) -> list[SeniorResponse]:
    """보호자 기준 어르신 목록을 조회합니다."""

    stmt = select(Senior).where(Senior.guardian_id == guardian_id)

    if active_only:
        stmt = stmt.where(Senior.active_flag.is_(True))

    stmt = stmt.order_by(Senior.created_at.desc())

    result = await session.execute(stmt)
    seniors = result.scalars().all()

    responses: list[SeniorResponse] = []

    for senior in seniors:
        response = await build_senior_response(
            session=session,
            senior=senior,
        )
        responses.append(response)

    return responses


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

    return await build_senior_response(
        session=session,
        senior=senior,
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

    for field_name, field_value in update_data.items():
        setattr(senior, field_name, field_value)

    await session.commit()
    await session.refresh(senior)

    return await build_senior_response(
        session=session,
        senior=senior,
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
