"""호스팅 요청/응답 DTO."""

from pydantic import BaseModel


class HostingCreateRequest(BaseModel):
    """호스팅 신청 요청."""

    senior_id: str
    date: str
    time_slot: str  # "점심" | "저녁"
    menu: str
    max_guests: int = 2  # 2~4명
    note: str = ""


class HostingResponse(BaseModel):
    """호스팅 정보 응답."""

    id: str
    senior_id: str
    senior_name: str
    district: str
    date: str
    time_slot: str
    menu: str
    max_guests: int
    status: str
    matched_volunteer_ids: list[str] = []
