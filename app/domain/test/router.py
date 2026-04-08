"""SMS 서비스 테스트용 라우터.

개발/QA 목적의 임시 엔드포인트입니다. 실제 운영 트리거(호스팅 신청/체크인 등)와
무관하게 sms 서비스 함수를 직접 호출해 발송 여부를 확인합니다.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.hosting.models import Hosting
from app.domain.senior.models import Senior
from app.domain.user.models import User
from app.services import sms as sms_service
from app.services.sms import send_auth_sms, send_sms

router = APIRouter()


class AuthSmsRequest(BaseModel):
    receiver_phone: str
    auth_code: str = "123456"


class NotificationSmsRequest(BaseModel):
    hosting_id: int
    receiver_id: int
    alarm_type: str  # match | checkin | update
    volunteer_id: int | None = None
    use_long_message: bool = False


class SeedRequest(BaseModel):
    receiver_phone: str  # 보호자(수신자) 실제 번호 — 본인 번호 권장
    volunteer_phone: str | None = None


@router.post("/sms/seed")
async def seed_sms_test_data(
    payload: SeedRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """알림 SMS 테스트용 더미 데이터를 생성합니다.

    보호자 User → 어르신 Senior → 호스팅 Hosting → 봉사자 User 순으로 만들고
    생성된 ID들을 반환합니다. 반환된 hosting_id/receiver_id/volunteer_id를
    아래 알림 SMS 폼에 그대로 입력하면 됩니다.
    """
    suffix = datetime.now().strftime("%Y%m%d%H%M%S")

    guardian = User(
        name="테스트보호자",
        email=f"test-guardian-{suffix}@example.com",
        password="x",
        phone_number=payload.receiver_phone,
        address="테스트 주소",
        user_role="guardian",
        cert_flag="approved",
    )
    db.add(guardian)
    await db.flush()

    volunteer = User(
        name="테스트봉사자",
        email=f"test-volunteer-{suffix}@example.com",
        password="x",
        # 봉사자 phone은 SMS 수신에 쓰이지 않지만, 잘못된 트리거로 발송될 위험을 막기 위해
        # 별도 입력이 없으면 보호자(receiver)와 동일한 번호로 둔다.
        phone_number=payload.volunteer_phone or payload.receiver_phone,
        address="테스트 주소",
        user_role="volunteer",
        cert_flag="approved",
    )
    db.add(volunteer)
    await db.flush()

    senior = Senior(
        guardian_id=guardian.user_id,
        name="테스트어르신",
        gender="여",
        age=80,
        address="테스트 주소",
        max_people=2,
    )
    db.add(senior)
    await db.flush()

    hosting = Hosting(
        senior_id=senior.senior_id,
        menu="된장찌개",
        hosting_time=datetime.now(timezone.utc) + timedelta(days=1),
        max_people=2,
    )
    db.add(hosting)
    await db.flush()

    await db.commit()

    return {
        "hosting_id": hosting.hosting_id,
        "receiver_id": guardian.user_id,
        "volunteer_id": volunteer.user_id,
        "senior_id": senior.senior_id,
    }


@router.post("/sms/auth")
async def test_auth_sms(payload: AuthSmsRequest) -> dict:
    """인증 SMS 발송 테스트 (DB 불필요)."""
    ok = await send_auth_sms(payload.receiver_phone, payload.auth_code)
    if not ok:
        raise HTTPException(status_code=500, detail="SMS 발송 실패")
    return {"success": True}


async def _db_get_user_by_id(db: AsyncSession, user_id: int) -> dict | None:
    """get_user_by_id stub 우회용 임시 조회 함수."""
    result = await db.execute(select(User).where(User.user_id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        return None
    return {
        "user_id": user.user_id,
        "name": user.name,
        "phone_number": user.phone_number,
    }


@router.post("/sms/notification")
async def test_notification_sms(
    payload: NotificationSmsRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """호스팅 알림 SMS 발송 테스트 (DB에 hosting/user 데이터 필요).

    `app.domain.user.service.get_user_by_id`가 아직 stub이므로 테스트 동안만
    DB 직접 조회 함수로 모킹합니다. 실제 구현이 들어오면 이 모킹은 자동으로 무의미해집니다.
    """

    async def _patched(user_id):  # noqa: ANN001 - 원본 시그니처 유지
        return await _db_get_user_by_id(db, user_id)

    with patch.object(sms_service, "get_user_by_id", _patched):
        ok = await send_sms(
            db=db,
            hosting_id=payload.hosting_id,
            receiver_id=payload.receiver_id,
            alarm_type=payload.alarm_type,
            volunteer_id=payload.volunteer_id,
            use_long_message=payload.use_long_message,
        )
    if not ok:
        raise HTTPException(status_code=500, detail="SMS 발송 실패 (수신자 정보/발송 오류 확인)")
    return {"success": True}
