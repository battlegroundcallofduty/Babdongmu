"""호스팅 SQLAlchemy ORM 모델."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Hosting(Base):
    __tablename__ = "hostings"

    hosting_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.senior_id", ondelete="RESTRICT"))
    menu: Mapped[str] = mapped_column(String(255))
    hosting_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    hosting_end: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    max_people: Mapped[int] = mapped_column(
        Integer, default=2
    )  # seniors.max_people이 기본값, 수정 가능 (2~4)
    hosting_status: Mapped[str] = mapped_column(
        String(20), default="신청가능"
    )  # 신청가능 | 모집완료 | 신청불가
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    visited_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)


class SmsLog(Base):
    """SMS 발송 이력.

    수신자가 여러 명인 경우 수신자별로 row 생성.
    alarm_type: match | checkin | checkout | update
    """

    __tablename__ = "sms_logs"

    sms_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hosting_id: Mapped[int] = mapped_column(ForeignKey("hostings.hosting_id", ondelete="CASCADE"))
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    is_send: Mapped[bool] = mapped_column(Boolean, default=False)
    alarm_type: Mapped[str] = mapped_column(String(20))  # match | checkin | checkout | update
    contents: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
