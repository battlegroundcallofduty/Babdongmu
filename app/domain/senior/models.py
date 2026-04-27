"""Senior SQLAlchemy ORM 모델."""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Senior(Base):
    """어르신 정보를 저장하는 모델입니다."""

    __tablename__ = "seniors"
    __table_args__ = (
        CheckConstraint("age >= 65", name="ck_senior_age"),
        CheckConstraint("max_people >= 2", name="ck_senior_max_people"),
    )

    senior_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guardian_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)

    address_id: Mapped[int] = mapped_column(
        ForeignKey("addresses.address_id"), unique=True, nullable=False
    )

    special_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    active_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    max_people: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    qr_code: Mapped[str | None] = mapped_column(String(500), nullable=True)

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
