"""매칭 요청/응답 DTO."""

from pydantic import BaseModel


class MatchCreateRequest(BaseModel):
    """매칭 신청 요청."""

    hosting_id: str


class MatchResponse(BaseModel):
    """매칭 정보 응답."""

    id: str
    hosting_id: str
    volunteer_id: str
    status: str
    checkin_at: str | None = None
    checkout_at: str | None = None
    volunteer_hours: float
