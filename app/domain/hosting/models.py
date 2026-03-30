"""호스팅 MongoDB 문서 스키마."""

from datetime import datetime, timezone


def hosting_document(
    senior_id: str,
    date: str,
    time_slot: str,
    menu: str,
    note: str = "",
) -> dict:
    """호스팅 문서를 생성합니다."""
    return {
        "senior_id": senior_id,
        "date": date,
        "time_slot": time_slot,
        "menu": menu,
        "note": note,
        "status": "pending",  # pending -> approved -> matched -> completed | cancelled
        "matched_volunteer_id": None,
        "created_at": datetime.now(timezone.utc),
    }
