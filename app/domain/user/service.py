"""유저 비즈니스 로직."""


async def create_user(email: str, password: str, name: str, phone: str, role: str, district: str) -> dict:
    """유저를 생성합니다."""
    pass


async def authenticate_user(email: str, password: str) -> dict | None:
    """이메일과 비밀번호로 유저를 인증합니다."""
    pass


async def get_user_by_email(email: str) -> dict | None:
    """이메일로 유저를 조회합니다."""
    pass


async def get_user_by_id(user_id: str) -> dict | None:
    """ID로 유저를 조회합니다."""
    pass
