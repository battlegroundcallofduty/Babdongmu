"""유저 SQLAlchemy ORM 모델."""

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import TIMESTAMP, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserRole(enum.Enum):
    VOLUNTEER = "volunteer"
    GUARDIAN = "guardian"
    ADMIN = "admin"


class CertFlag(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # 카카오 로그인 시 None
    phone_number: Mapped[str] = mapped_column(String(20))
    address: Mapped[str] = mapped_column(String(255))
    user_role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    cert_flag: Mapped[CertFlag] = mapped_column(Enum(CertFlag), default=CertFlag.PENDING)
    cert_reject_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )


class DocumentType(enum.Enum):
    CRIMINAL_RECORD = "criminal_record"   # 봉사자: 범죄경력조회서
    WELFARE_CERT = "welfare_cert"         # 보호자: 복지관 인증서류
    FAMILY_CERT = "family_cert"           # 보호자: 가족관계증명서
    IDENTITY_COPY = "identity_copy"       # 공통: 신분증 사본


class Document(Base):
    """신원 서류. 봉사자/보호자 가입 시 업로드."""

    __tablename__ = "documents"

    document_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    document_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType))
    document_url: Mapped[str] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
