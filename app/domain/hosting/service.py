"""호스팅 비즈니스 로직."""


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
