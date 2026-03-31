"""AI 요청/응답 DTO."""

from pydantic import BaseModel


class AiSummaryResponse(BaseModel):
    """AI 소개글 응답."""

    senior_id: str
    summary: str
    updated_at: str | None = None
