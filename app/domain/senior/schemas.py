"""어르신 요청/응답 스키마."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.senior.models import GenderEnum


class SeniorCreateRequest(BaseModel):
    """어르신 등록 요청 스키마입니다."""

    name: str = Field(..., min_length=1, max_length=100, description="어르신 이름")
    gender: GenderEnum = Field(..., description="성별")
    age: int = Field(..., ge=65, description="어르신 나이")

    road_address: str = Field(..., min_length=1, max_length=255, description="도로명 주소")
    jibun_address: str | None = Field(default=None, max_length=255, description="지번 주소")
    zonecode: str | None = Field(default=None, max_length=10, description="우편번호")
    sigungu: str = Field(..., min_length=1, max_length=100, description="시군구")
    bname: str | None = Field(default=None, max_length=100, description="법정동명")
    detail_address: str = Field(..., min_length=1, max_length=255, description="상세 주소")

    sido: str | None = Field(default=None, max_length=50, description="시도")
    building_name: str | None = Field(default=None, max_length=100, description="건물명")
    is_apartment: bool | None = Field(default=None, description="아파트 여부")
    lat: float | None = Field(default=None, description="위도")
    lng: float | None = Field(default=None, description="경도")
    sigungu_code: str | None = Field(default=None, max_length=20, description="시군구 코드")

    special_note: str | None = Field(default=None, description="특이사항")
    active_flag: bool = Field(default=True, description="활성 여부")
    max_people: int = Field(..., ge=2, le=4, description="최대 동행 인원")


class SeniorUpdateRequest(BaseModel):
    """어르신 수정 요청 스키마입니다."""

    name: str | None = Field(default=None, min_length=1, max_length=100, description="어르신 이름")
    gender: GenderEnum | None = Field(default=None, description="성별")
    age: int | None = Field(default=None, ge=65, description="어르신 나이")

    road_address: str | None = Field(default=None, min_length=1, max_length=255, description="도로명 주소")
    jibun_address: str | None = Field(default=None, max_length=255, description="지번 주소")
    zonecode: str | None = Field(default=None, max_length=10, description="우편번호")
    sigungu: str | None = Field(default=None, min_length=1, max_length=100, description="시군구")
    bname: str | None = Field(default=None, max_length=100, description="법정동명")
    detail_address: str | None = Field(default=None, min_length=1, max_length=255, description="상세 주소")

    sido: str | None = Field(default=None, max_length=50, description="시도")
    building_name: str | None = Field(default=None, max_length=100, description="건물명")
    is_apartment: bool | None = Field(default=None, description="아파트 여부")
    lat: float | None = Field(default=None, description="위도")
    lng: float | None = Field(default=None, description="경도")
    sigungu_code: str | None = Field(default=None, max_length=20, description="시군구 코드")

    special_note: str | None = Field(default=None, description="특이사항")
    active_flag: bool | None = Field(default=None, description="활성 여부")
    max_people: int | None = Field(default=None, ge=2, le=4, description="최대 동행 인원")


class SeniorResponse(BaseModel):
    """어르신 응답 스키마입니다."""

    senior_id: int
    guardian_id: int
    name: str
    gender: GenderEnum
    age: int

    road_address: str
    jibun_address: str | None
    zonecode: str | None
    sigungu: str
    bname: str | None
    detail_address: str

    sido: str | None
    building_name: str | None
    is_apartment: bool | None
    lat: float | None
    lng: float | None
    sigungu_code: str | None

    special_note: str | None
    active_flag: bool
    ai_summary: str | None
    max_people: int
    qr_code: str | None
    full_hosting_count: int = 0
    total_hosting_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)