"""매칭 SQLAlchemy ORM 모델."""

from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MatchingInfo(Base):
    __tablename__ = "matching_info"
    __table_args__ = (
        # cancelled 상태 제외하고 (hosting_id, vt_id) 중복 방지
        Index(
            "uix_hosting_vt_active",
            "hosting_id",
            "vt_id",
            unique=True,
            sqlite_where=text("match_status != 'cancelled'"),
        ),
    )

    matching_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hosting_id: Mapped[int] = mapped_column(ForeignKey("hostings.hosting_id", ondelete="CASCADE"))
    vt_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))  # 봉사자
    senior_id: Mapped[int] = mapped_column(  # 어르신
        ForeignKey("seniors.senior_id", ondelete="CASCADE")
    )
    # pending | approved | rejected | cancelled
    match_status: Mapped[str] = mapped_column(String(20), default="pending")
    check_in_time: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    check_out_time: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
