"""매칭 MongoDB 문서 스키마."""

from datetime import datetime, timezone


def match_document(
    hosting_id: str,
    volunteer_id: str,
) -> dict:
    """매칭 문서를 생성합니다."""
    return {
        "hosting_id": hosting_id,
        "volunteer_id": volunteer_id,
        "status": "scheduled",  # scheduled -> in_progress -> completed | no_show
        "checkin_at": None,
        "checkout_at": None,
        "volunteer_hours": 0.0,
        "created_at": datetime.now(timezone.utc),
    }
