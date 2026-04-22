"""호스팅 비즈니스 로직."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.hosting.models import AlarmType, Hosting, HostingStatus
from app.domain.hosting.schemas import HostingCreateRequest, HostingResponse
from app.domain.match.models import MatchingInfo, MatchStatus
from app.domain.senior.models import Senior
from app.services.sms import send_sms

logger = logging.getLogger(__name__)


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



def ensure_utc_aware(dt: datetime) -> datetime:
    """datetime을 UTC aware 형태로 맞춥니다."""

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)



def process_hosting_status_by_time(
    hosting: Hosting,
) -> HostingStatus | None:
    """호스팅 1건의 시간 기반 다음 상태를 계산합니다."""

    now = get_now_utc()
    hosting_at = ensure_utc_aware(hosting.hosting_at)
    hosting_end = ensure_utc_aware(hosting.hosting_end)
    deadline_at = hosting_at - timedelta(hours=12)
    current_status = hosting.hosting_status

    # 1. 시작 12시간 전까지 모집 미달이면 실패
    if now >= deadline_at and current_status == HostingStatus.OPEN:
        return HostingStatus.FAILED

    # 2. 시작 12시간 전이고 모집완료 상태면 확정
    if now >= deadline_at and current_status == HostingStatus.FULL:
        return HostingStatus.FIXED

    # 3. 시작 시각이 되었고 확정 상태면 진행중으로 변경
    if now >= hosting_at and current_status == HostingStatus.FIXED:
        return HostingStatus.IN_PROGRESS

    # 4. 종료 시점 처리
    if now >= hosting_end:
        if current_status == HostingStatus.IN_PROGRESS:
            return HostingStatus.CLOSED

        if current_status in {
            HostingStatus.OPEN,
            HostingStatus.FULL,
            HostingStatus.FIXED,
        }:
            return HostingStatus.FAILED

    return None


async def get_approved_volunteer_ids(
    session: AsyncSession,
    hosting_id: int,
) -> list[int]:
    """호스팅에 APPROVED 상태인 봉사자 ID 목록을 반환합니다."""
    result = await session.execute(
        select(MatchingInfo.vt_id).where(
            MatchingInfo.hosting_id == hosting_id,
            MatchingInfo.match_status == MatchStatus.APPROVED,
        )
    )
    return list(result.scalars().all())


async def mark_matches_not_visited(
    session: AsyncSession,
    hosting_id: int,
) -> int:
    """호스팅의 미방문 매칭을 NOT_VISITED로 변경합니다."""

    stmt = select(MatchingInfo).where(
        MatchingInfo.hosting_id == hosting_id,
        MatchingInfo.match_status == MatchStatus.APPROVED,
    )
    result = await session.execute(stmt)
    matches = result.scalars().all()

    changed_count = 0

    for match in matches:
        # 체크아웃이 없으면 미방문 처리
        # - 체크인 없음
        # - 체크인만 있고 체크아웃 없음
        if match.check_out_time is None:
            match.match_status = MatchStatus.NOT_VISITED
            changed_count += 1

    return changed_count


async def run_hosting_status_scheduler(
    session: AsyncSession,
) -> int:
    """시간 조건이 도래한 호스팅과 매칭 상태를 일괄 처리합니다."""

    stmt = select(Hosting).where(
        Hosting.hosting_status.in_(
            [
                HostingStatus.OPEN,
                HostingStatus.FULL,
                HostingStatus.FIXED,
                HostingStatus.IN_PROGRESS,
            ]
        )
    )

    result = await session.execute(stmt)
    hostings = result.scalars().all()

    changed_count = 0      # 호스팅 상태 변경 건수 (반환값 + 로그용)
    match_changed_count = 0  # 매칭 NOT_VISITED 처리 건수 (커밋 트리거용)
    # SMS 발송 대상 수집 (commit 전 APPROVED 상태일 때 조회)
    # hosting_id → (alarm_type, guardian_id, [vt_ids])
    notification_map: dict[int, tuple[AlarmType, int, list[int]]] = {}

    for hosting in hostings:
        new_status = process_hosting_status_by_time(hosting=hosting)
        if new_status is None:
            continue

        if hosting.hosting_status != new_status:
            prev_status = hosting.hosting_status
            hosting.hosting_status = new_status
            changed_count += 1
            logger.info(
                "호스팅 ID=%d 상태 전환: %s → %s",
                hosting.hosting_id, prev_status, new_status,
            )

        if new_status in {HostingStatus.FAILED, HostingStatus.FIXED}:
            vt_ids = await get_approved_volunteer_ids(session, hosting.hosting_id)
            senior = await session.get(Senior, hosting.senior_id)
            alarm_type = AlarmType.DELETE if new_status == HostingStatus.FAILED else AlarmType.MATCH
            notification_map[hosting.hosting_id] = (alarm_type, senior.guardian_id, vt_ids)

        if new_status in {HostingStatus.FAILED, HostingStatus.CLOSED}:
            match_changed_count += await mark_matches_not_visited(
                session=session,
                hosting_id=hosting.hosting_id,
            )

    if changed_count > 0:
        await session.commit()
        logger.info("스케줄러 커밋 완료: 호스팅 %d건 상태 변경", changed_count)
    sms_tasks = []

    # 보호자 + 봉사자 전원에게 알림 (FAILED: 무산, FIXED: 매칭 확정)
    for hid, (alarm_type, guardian_id, vt_ids) in notification_map.items():
        sms_tasks.append(
            send_sms(
                db=session,
                hosting_id=hid,
                receiver_id=guardian_id,
                alarm_type=alarm_type,
                use_long_message=True,
            )
        )
        for vt_id in vt_ids:
            sms_tasks.append(
                send_sms(
                    db=session,
                    hosting_id=hid,
                    receiver_id=vt_id,
                    alarm_type=alarm_type,
                    use_long_message=True,
                )
            )

    results = await asyncio.gather(*sms_tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            logger.warning("SMS 발송 실패: %s", result)

    if sms_tasks:
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

    hosting_at = ensure_utc_aware(request.hosting_at)
    hosting_end = ensure_utc_aware(request.hosting_end)

    hosting = Hosting(
        senior_id=senior.senior_id,
        menu=request.menu,
        hosting_at=hosting_at,
        hosting_end=hosting_end,
        max_people=hosting_max_people,
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

    if hosting.hosting_status in {
        HostingStatus.FIXED,
        HostingStatus.IN_PROGRESS,
        HostingStatus.CLOSED,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="호스팅 확정 / 진행 중 / 완료 시에는 취소할 수 없습니다.",
        )

    hosting.hosting_status = HostingStatus.FAILED

    # commit 전 APPROVED 봉사자 목록 수집
    vt_ids = await get_approved_volunteer_ids(session, hosting_id)

    await session.commit()
    await session.refresh(hosting)

    # SMS 발송 — 신청한 봉사자 전원에게 호스팅 취소 알림
    sms_tasks = []
    for vt_id in vt_ids:
        sms_tasks.append(
            send_sms(
                db=session,
                hosting_id=hosting_id,
                receiver_id=vt_id,
                alarm_type=AlarmType.DELETE,
                use_long_message=True,
            )
        )
    results = await asyncio.gather(*sms_tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            logger.warning("SMS 발송 실패: %s", result)

    if sms_tasks:
        await session.commit()

    return HostingResponse.model_validate(hosting)
