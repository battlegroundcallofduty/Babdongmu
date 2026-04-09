"""매칭 SQLAlchemy ORM 모델."""

from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MatchingInfo(Base):
    __tablename__ = "matching_info"
    __table_args__ = (
        UniqueConstraint("hosting_id", "vt_id"),
    )

    matching_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hosting_id: Mapped[int] = mapped_column(ForeignKey("hostings.hosting_id", ondelete="CASCADE"))
    vt_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))  # 봉사자
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.senior_id", ondelete="CASCADE"))  # 어르신
    is_apply: Mapped[bool] = mapped_column(Boolean, default=True)    # 신청/취소 여부
    check_in: Mapped[bool] = mapped_column(Boolean, default=False)   # 체크인 여부
    check_in_time: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    check_out_time: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )