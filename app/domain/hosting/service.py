"""호스팅 비즈니스 로직."""

# 매칭 인원 정책:
# - 호스팅당 봉사자 최소 2명, 최대 4명 (max_guests: 2~4)
# - 매칭 신청 시 len(matched_volunteer_ids) < max_guests 이면 "모집중"
# - len(matched_volunteer_ids) == max_guests 이면 "모집완료"
# - 최소 2명은 안전상 고정 (1:1 단독 방문 방지)


async def create_hosting(data: dict) -> dict:
    """호스팅을 생성합니다."""
    pass


async def list_hostings(district: str | None = None, status: str | None = None) -> list[dict]:
    """호스팅 목록을 조회합니다."""
    pass


async def get_hosting_by_id(hosting_id: str) -> dict | None:
    """ID로 호스팅을 조회합니다."""
    pass


async def approve_hosting(hosting_id: str) -> dict | None:
    """호스팅을 승인합니다."""
    pass
