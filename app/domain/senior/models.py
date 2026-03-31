"""어르신 MongoDB 문서 스키마."""

from datetime import datetime, timezone


def senior_document(
    name: str,
    age: int,
    address: str,
    district: str,
    available_days: list[str],
    available_time: str,
    registered_by: str,
    note: str = "",
) -> dict:
    """어르신 문서를 생성합니다."""
    return {
        "name": name,
        "age": age,
        "address": address,
        "district": district,
        "available_days": available_days,
        "available_time": available_time,
        "registered_by": registered_by,
        "note": note,
        "is_active": True,
        "ai_summary": "",
        "ai_summary_updated_at": None,
        "created_at": datetime.now(timezone.utc),
    }
