"""후기 요청/응답 DTO."""

from pydantic import BaseModel


class ReviewCreateRequest(BaseModel):
    """후기 작성 요청."""

    match_id: str
    message: str


class ReviewResponse(BaseModel):
    """후기 응답."""

    id: str
    match_id: str
    volunteer_id: str
    volunteer_name: str
    message: str
    created_at: str
