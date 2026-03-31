"""어르신 비즈니스 로직."""


async def create_senior(data: dict, registered_by: str) -> dict:
    """어르신을 등록합니다."""
    pass


async def list_seniors(district: str | None = None) -> list[dict]:
    """어르신 목록을 조회합니다."""
    pass


async def get_senior_by_id(senior_id: str) -> dict | None:
    """ID로 어르신을 조회합니다."""
    pass


async def update_senior(senior_id: str, data: dict) -> dict | None:
    """어르신 정보를 수정합니다."""
    pass
