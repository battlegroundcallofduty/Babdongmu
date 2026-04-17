"""호스팅 요청/응답 스키마."""

from datetime import datetime, time, timedelta

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.hosting.models import HostingStatus


class HostingCreateRequest(BaseModel):
    """호스팅 등록 요청 스키마입니다."""

    senior_id: int = Field(..., ge=1, description="어르신 ID")
    menu: str = Field(..., min_length=1, max_length=255, description="메뉴")
    hosting_at: datetime = Field(..., description="호스팅 시작 일시")
    hosting_end: datetime = Field(..., description="호스팅 종료 일시")
    max_people: int | None = Field(
        default=None,
        ge=2,
        le=4,
        description="모집 가능 인원 (미입력 시 어르신 기본값 사용)",
    )

    @model_validator(mode="after")
    def validate_hosting_time(self) -> "HostingCreateRequest":
        """호스팅 시간 규칙을 검증합니다."""

        if self.hosting_at.time() < time(7, 0):
            raise ValueError("호스팅 시작 시각은 07:00 이후여야 합니다.")

        min_end_time = self.hosting_at + timedelta(hours=2)
        max_end_time = self.hosting_at + timedelta(hours=4)

        if self.hosting_end < min_end_time:
            raise ValueError("호스팅 종료 일시는 시작 일시보다 최소 2시간 늦어야 합니다.")

        if self.hosting_end > max_end_time:
            raise ValueError("호스팅 종료 일시는 시작 일시보다 최대 4시간까지만 가능합니다.")

        if self.hosting_end.time() > time(22, 0):
            raise ValueError("호스팅 종료 시각은 22:00를 넘을 수 없습니다.")

        return self


class HostingUpdateRequest(BaseModel):
    """호스팅 수정 요청 스키마입니다."""

    menu: str | None = Field(default=None, min_length=1, max_length=255, description="메뉴")
    hosting_at: datetime | None = Field(default=None, description="호스팅 시작 일시")
    hosting_end: datetime | None = Field(default=None, description="호스팅 종료 일시")
    max_people: int | None = Field(default=None, ge=2, le=4, description="모집 가능 인원")

    @model_validator(mode="after")
    def validate_hosting_time(self) -> "HostingUpdateRequest":
        """호스팅 시간 규칙을 검증합니다."""

        if self.hosting_at is None and self.hosting_end is None:
            return self

        if self.hosting_at is None or self.hosting_end is None:
            return self

        if self.hosting_at.time() < time(7, 0):
            raise ValueError("호스팅 시작 시각은 07:00 이후여야 합니다.")

        min_end_time = self.hosting_at + timedelta(hours=2)
        max_end_time = self.hosting_at + timedelta(hours=4)

        if self.hosting_end < min_end_time:
            raise ValueError("호스팅 종료 일시는 시작 일시보다 최소 2시간 늦어야 합니다.")

        if self.hosting_end > max_end_time:
            raise ValueError("호스팅 종료 일시는 시작 일시보다 최대 4시간까지만 가능합니다.")

        if self.hosting_end.time() > time(22, 0):
            raise ValueError("호스팅 종료 시각은 22:00를 넘을 수 없습니다.")

        return self


class HostingResponse(BaseModel):
    """호스팅 응답 스키마입니다."""

    hosting_id: int
    senior_id: int
    menu: str
    hosting_at: datetime
    hosting_end: datetime
    max_people: int
    hosting_status: HostingStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
