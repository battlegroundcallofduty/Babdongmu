"""후기 비즈니스 로직."""


async def create_review(match_id: str, volunteer_id: str, message: str) -> dict:
    """후기를 작성합니다."""
    pass


async def list_reviews_by_senior(senior_id: str) -> list[dict]:
    """어르신별 후기를 조회합니다."""
    pass
