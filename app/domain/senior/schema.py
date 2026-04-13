"""어르신 요청/응답 스키마."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.senior.models import GenderEnum


class SeniorCreateRequest(BaseModel):
    """어르신 등록 요청 스키마입니다."""

    name: str = Field(..., min_length=1, max_length=100, description="어르신 이름")
    gender: GenderEnum = Field(..., description="성별")
    age: int = Field(..., ge=65, description="어르신 나이")
    address: str = Field(..., min_length=1, max_length=255, description="주소")
    special_note: str | None = Field(default=None, description="특이사항")
    active_flag: bool = Field(default=True, description="활성 여부")
    ai_summary: str | None = Field(default=None, description="어르신 AI 요약")
    max_people: int = Field(..., default=2, ge=2, le=4, description="최대 동행 인원")
    qr_code: str | None = Field(default=None, max_length=500, description="QR 코드 값")


class SeniorUpdateRequest(BaseModel):
    """어르신 수정 요청 스키마입니다."""

    name: str | None = Field(default=None, min_length=1, max_length=100, description="어르신 이름")
    gender: GenderEnum | None = Field(default=None, description="성별")
    age: int | None = Field(default=None, ge=65, description="어르신 나이")
    address: str | None = Field(default=None, min_length=1, max_length=255, description="주소")
    special_note: str | None = Field(default=None, description="특이사항")
    active_flag: bool | None = Field(default=None, description="활성 여부")
    ai_summary: str | None = Field(default=None, description="어르신 AI 요약")
    max_people: int | None = Field(default=None, ge=2, le=4, description="최대 동행 인원")
    qr_code: str | None = Field(default=None, max_length=500, description="QR 코드 값")


class SeniorResponse(BaseModel):
    """어르신 응답 스키마입니다."""

    senior_id: int
    guardian_id: int
    name: str
    gender: GenderEnum
    age: int
    address: str
    special_note: str | None
    active_flag: bool
    ai_summary: str | None
    max_people: int
    qr_code: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

