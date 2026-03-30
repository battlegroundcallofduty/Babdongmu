"""호스팅 MongoDB 문서 스키마."""

from datetime import datetime, timezone


def hosting_document(
    senior_id: str,
    date: str,
    time_slot: str,
    menu: str,
    max_guests: int = 2,
    note: str = "",
) -> dict:
    """호스팅 문서를 생성합니다."""
    if not 2 <= max_guests <= 4:
        raise ValueError("모집 인원은 2~4명이어야 합니다.")
    return {
        "senior_id": senior_id,
        "date": date,
        "time_slot": time_slot,
        "menu": menu,
        "max_guests": max_guests,
        "note": note,
        "status": "pending",  # pending -> approved -> matched -> completed | cancelled
        "matched_volunteer_ids": [],
        "created_at": datetime.now(timezone.utc),
    }
