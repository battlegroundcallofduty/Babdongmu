"""유저 비즈니스 로직."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user.models import User


async def get_user_by_id(user_id: int, db: AsyncSession) -> User | None:
    """ID로 유저를 조회합니다."""
    result = await db.execute(select(User).where(User.user_id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    """이메일로 유저를 조회합니다."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(email: str, password: str, name: str, phone: str, role: str, address: str) -> dict:
    """유저를 생성합니다."""
    pass


async def authenticate_user(email: str, password: str) -> dict | None:
    """이메일과 비밀번호로 유저를 인증합니다."""
    pass
