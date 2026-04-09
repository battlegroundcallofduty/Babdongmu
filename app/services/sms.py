"""SMS 발송 유틸리티.

차후 Solapi 이외의 api 사용을 고려하여 추상화 레이어로 작성하였습니다
함수 명명 : 타 업체 api추가시 _send_via_업체명api() 사용
"""

import asyncio

from solapi import SolapiMessageService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.domain.hosting.models import AlarmType, Hosting, SmsLog
from app.domain.user.service import get_user_by_id


async def send_sms(
    db: AsyncSession,
    hosting_id: int,
    receiver_id: int,
    alarm_type: AlarmType,
    volunteer_id: int | None = None,
    use_long_message: bool = False,
) -> bool:
    """SMS를 발송하고 발송 이력을 DB에 기록합니다.

    Args:
        db: 데이터베이스 세션
        hosting_id: 호스팅 ID
        receiver_id: 수신자 ID (보호자 등)
        alarm_type: AlarmType Enum (MATCH / CHECKIN / CHECKOUT / UPDATE)
        volunteer_id: 봉사자 ID (MATCH, CHECKIN, CHECKOUT에서 필요)
        use_long_message: True면 장문(LMS), False면 단문(SMS)
    """
    # 수신자 정보 조회
    receiver = await get_user_by_id(receiver_id)
    if not receiver or not receiver.get("phone_number"):
        print(f"[SMS] 수신자 {receiver_id}의 전화번호를 찾을 수 없습니다.")
        return False

    to = receiver["phone_number"]

    # 호스팅 정보 조회 (장문에서 필요)
    hosting = None
    if use_long_message:
        result = await db.execute(select(Hosting).where(Hosting.hosting_id == hosting_id))
        hosting = result.scalar_one_or_none()

    # 메시지 생성
    if alarm_type == AlarmType.MATCH:
        volunteer_name = "봉사자"
        if volunteer_id:
            volunteer = await get_user_by_id(volunteer_id)
            volunteer_name = volunteer.get("name") if volunteer else "봉사자"

        if use_long_message and hosting:
            time_str = hosting.hosting_at.strftime("%m월 %d일 %H:%M")
            message = (
                f"[밥동무 호스팅 신청]\n\n"
                f"{volunteer_name}님이 호스팅을 신청했습니다.\n\n"
                f"메뉴: {hosting.menu}\n"
                f"일시: {time_str}"
            )
        else:
            message = f"[밥동무] {volunteer_name}님이 호스팅을 신청했습니다."

    elif alarm_type == AlarmType.CHECKIN:
        volunteer_name = "봉사자"
        if volunteer_id:
            volunteer = await get_user_by_id(volunteer_id)
            volunteer_name = volunteer.get("name") if volunteer else "봉사자"

        if use_long_message and hosting:
            time_str = hosting.hosting_at.strftime("%m월 %d일 %H:%M")
            message = (
                f"[밥동무 방문 체크인]\n\n"
                f"{volunteer_name}님이 방문 체크인했습니다.\n\n"
                f"메뉴: {hosting.menu}\n"
                f"일시: {time_str}"
            )
        else:
            message = f"[밥동무] {volunteer_name}님이 방문 체크인했습니다."

    elif alarm_type == AlarmType.UPDATE:
        if use_long_message and hosting:
            time_str = hosting.hosting_at.strftime("%m월 %d일 %H:%M")
            message = (
                f"[밥동무 호스팅 수정]\n\n"
                f"호스팅 정보가 수정되었습니다.\n\n"
                f"메뉴: {hosting.menu}\n"
                f"일시: {time_str}\n\n"
                f"접속하여 상세 정보를 확인해주세요."
            )
        else:
            message = "[밥동무] 호스팅 정보가 수정되었습니다. 확인해주세요."

    elif alarm_type == AlarmType.CHECKOUT:
        volunteer_name = "봉사자"
        if volunteer_id:
            volunteer = await get_user_by_id(volunteer_id)
            volunteer_name = volunteer.get("name") if volunteer else "봉사자"

        if use_long_message and hosting:
            time_str = hosting.hosting_at.strftime("%m월 %d일 %H:%M")
            message = (
                f"[밥동무 방문 완료]\n\n"
                f"{volunteer_name}님의 방문이 완료되었습니다.\n\n"
                f"메뉴: {hosting.menu}\n"
                f"일시: {time_str}"
            )
        else:
            message = f"[밥동무] {volunteer_name}님의 방문이 완료되었습니다."

    else:
        message = "[밥동무] 알림이 있습니다."

    # SMS 발송
    is_send = await _send_via_solapi(to, message)

    log = SmsLog(
        hosting_id=hosting_id,
        receiver_id=receiver_id,
        is_send=is_send,
        alarm_type=alarm_type,
        contents=message,
    )
    db.add(log)
    await db.commit()

    return is_send


async def send_auth_sms(receiver_phone: str, auth_code: str) -> bool:
    """인증용 SMS를 발송합니다 (이력 기록 없음).

    Args:
        receiver_phone: 수신 번호
        auth_code: 인증 코드 (6자리 숫자 등)

    Returns:
        발송 성공 여부
    """
    message = f"[밥동무] 인증번호: {auth_code}\n\n3분 이내에 입력해주세요."

    # SMS 발송 (DB 로깅 없음)
    return await _send_via_solapi(receiver_phone, message)


# ---------------------------------------------------------------------------
# Solapi 구현체
# ---------------------------------------------------------------------------


async def _send_via_solapi(to: str, message: str) -> bool:
    """Solapi로 SMS를 발송합니다.

    Solapi SDK는 동기 방식이므로 asyncio.to_thread로 감싸 이벤트 루프 블로킹을 방지합니다.
    """
    if not settings.SOLAPI_API_KEY:
        print(f"[SMS:Solapi 미설정] to={to}, message={message}")
        return False

    def _send() -> None:
        from solapi.model import RequestMessage

        service = SolapiMessageService(
            api_key=settings.SOLAPI_API_KEY,
            api_secret=settings.SOLAPI_API_SECRET,
        )
        service.send(
            RequestMessage(
                to=to,
                from_=settings.SOLAPI_SENDER,
                text=message,
            )
        )

    try:
        await asyncio.to_thread(_send)
        return True
    except Exception as e:
        print(f"[SMS:Solapi 발송 실패] {e}")
        return False
