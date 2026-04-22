"""호스팅 SQLAlchemy ORM 모델."""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    CheckConstraint,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HostingStatus(str, enum.Enum):
    """호스팅 상태."""

    OPEN = "신청가능"
    FULL = "모집완료"
    FAILED = "취소"
    IN_PROGRESS = "진행중"
    CLOSED = "완료"


class AlarmType(str, enum.Enum):
    """SMS 알림 타입."""

    MATCH = "match"
    CHECKIN = "checkin"
    CHECKOUT = "checkout"
    UPDATE = "update"
    DELETE = "delete"


class Hosting(Base):
    """호스팅 정보를 저장하는 모델입니다."""

    __tablename__ = "hostings"
    __table_args__ = (
        CheckConstraint("max_people >= 2", name="ck_hosting_max_people"),
    )

    hosting_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    senior_id: Mapped[int] = mapped_column(
        ForeignKey("seniors.senior_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    menu: Mapped[str] = mapped_column(String(255), nullable=False)
    hosting_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    hosting_end: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    max_people: Mapped[int] = mapped_column(Integer, nullable=False)

    road_address: Mapped[str] = mapped_column(String(255), nullable=False)
    jibun_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    zonecode: Mapped[str | None] = mapped_column(String(10), nullable=True)
    sigungu: Mapped[str] = mapped_column(String(100), nullable=False)
    bname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    detail_address: Mapped[str] = mapped_column(String(255), nullable=False)

    sido: Mapped[str | None] = mapped_column(String(50), nullable=True)
    building_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_apartment: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    sigungu_code: Mapped[str | None] = mapped_column(String(20), nullable=True)

    hosting_status: Mapped[HostingStatus] = mapped_column(
        Enum(HostingStatus),
        nullable=False,
        default=HostingStatus.OPEN,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )



class SmsLog(Base):
    """SMS 발송 이력."""

    __tablename__ = "sms_logs"

    sms_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hosting_id: Mapped[int] = mapped_column(
        ForeignKey("hostings.hosting_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    receiver_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_send: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    alarm_type: Mapped[AlarmType] = mapped_column(Enum(AlarmType), nullable=False)
    contents: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
