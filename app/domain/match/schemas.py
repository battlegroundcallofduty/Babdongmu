"""매칭 Pydantic 스키마."""

from datetime import datetime

from pydantic import BaseModel

from app.domain.match.models import MatchStatus


class MatchResponse(BaseModel):
    """매칭 기본 응답 스키마."""

    matching_id: int
    hosting_id: int
    vt_id: int
    senior_id: int
    match_status: MatchStatus
    check_in_time: datetime | None
    check_out_time: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MyMatchResponse(BaseModel):
    """내 매칭 목록 조회 전용 응답 스키마."""

    matching_id: int
    match_status: MatchStatus
    check_in_time: datetime | None
    check_out_time: datetime | None

    # 호스팅 정보
    hosting_id: int
    menu: str
    hosting_at: datetime

    # 시니어 정보
    senior_id: int
    senior_name: str
    senior_address: str

    # 봉사시간
    actual_volunteer_time: int | None

    model_config = {"from_attributes": False}
