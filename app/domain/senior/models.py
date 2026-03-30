"""어르신 MongoDB 문서 스키마."""

from datetime import datetime, timezone


def senior_document(
    name: str,
    age: int,
    address: str,
    district: str,
    specialty_foods: list[str],
    available_days: list[str],
    available_time: str,
    guardian_id: str,
    note: str = "",
) -> dict:
    """어르신 문서를 생성합니다."""
    return {
        "name": name,
        "age": age,
        "address": address,
        "district": district,
        "specialty_foods": specialty_foods,
        "available_days": available_days,
        "available_time": available_time,
        "guardian_id": guardian_id,
        "note": note,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }
