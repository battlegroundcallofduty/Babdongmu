"""매칭 Pydantic 스키마."""

from datetime import datetime

from pydantic import BaseModel


class MatchResponse(BaseModel):
    matching_id: int
    hosting_id: int
    vt_id: int
    senior_id: int
    match_status: str
    check_in_time: datetime | None
    check_out_time: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
