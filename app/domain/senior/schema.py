"""어르신 요청/응답 DTO."""

from pydantic import BaseModel


class SeniorCreateRequest(BaseModel):
    """어르신 등록 요청 (보호자가 대리 등록)."""

    name: str
    age: int
    address: str
    district: str
    specialty_foods: list[str]
    available_days: list[str]
    available_time: str
    note: str = ""


class SeniorResponse(BaseModel):
    """어르신 정보 응답."""

    id: str
    name: str
    age: int
    district: str
    specialty_foods: list[str]
    available_days: list[str]
    available_time: str
    is_active: bool
