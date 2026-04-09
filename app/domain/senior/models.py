"""어르신 SQLAlchemy ORM 모델."""

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import TIMESTAMP, Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Senior(Base):
    __tablename__ = "seniors"

    senior_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guardian_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(String(100))
    gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum))
    age: Mapped[int] = mapped_column(Integer)
    address: Mapped[str] = mapped_column(String(255))
    special_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    active_flag: Mapped[bool] = mapped_column(Boolean, default=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    max_people: Mapped[int] = mapped_column(Integer, default=2)
    qr_code: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
