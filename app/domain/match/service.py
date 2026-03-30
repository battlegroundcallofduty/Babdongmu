"""매칭 비즈니스 로직."""


async def create_match(hosting_id: str, volunteer_id: str) -> dict:
    """매칭을 생성합니다."""
    pass


async def list_matches_by_volunteer(volunteer_id: str, status: str | None = None) -> list[dict]:
    """봉사자의 매칭 목록을 조회합니다."""
    pass


async def checkin(match_id: str) -> dict | None:
    """체크인 시간을 기록합니다."""
    pass


async def checkout(match_id: str) -> dict | None:
    """체크아웃 시간을 기록하고 봉사시간을 계산합니다."""
    pass
