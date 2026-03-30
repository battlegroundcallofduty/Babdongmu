"""후기 MongoDB 문서 스키마."""

from datetime import datetime, timezone


def review_document(
    match_id: str,
    volunteer_id: str,
    message: str,
) -> dict:
    """후기 문서를 생성합니다."""
    return {
        "match_id": match_id,
        "volunteer_id": volunteer_id,
        "message": message,
        "created_at": datetime.now(timezone.utc),
    }
