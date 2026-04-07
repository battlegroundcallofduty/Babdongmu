"""유저 SQLAlchemy ORM 모델."""

from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(20))
    address: Mapped[str] = mapped_column(String(255))
    user_role: Mapped[str] = mapped_column(String(20))           # volunteer | guardian | admin
    cert_flag: Mapped[str] = mapped_column(String(20), default="pending")  # pending | approved | rejected
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class Document(Base):
    """봉사자 신원 서류."""

    __tablename__ = "documents"

    document_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    document_url: Mapped[str] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
