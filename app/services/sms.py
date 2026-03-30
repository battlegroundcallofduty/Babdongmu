"""CoolSMS 발송 유틸리티."""

from app.config import settings


async def send_sms(to: str, message: str) -> bool:
    """SMS를 발송합니다. 성공 시 True를 반환합니다."""
    # CoolSMS API 연동 필요
    # API 키가 설정되지 않으면 로그만 출력
    if not settings.COOLSMS_API_KEY:
        print(f"[SMS 미설정] to={to}, message={message}")
        return False
    pass
