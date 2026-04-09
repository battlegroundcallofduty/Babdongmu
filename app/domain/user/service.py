"""유저 비즈니스 로직."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user.models import User


async def get_user_by_id(user_id: int, db: AsyncSession) -> User | None:
    """ID로 유저를 조회합니다."""
    # 유저 가져올때 서류 정보 가져와야 하면 추후 selectinload 추가될듯
    statement = select(User).where(User.user_id == user_id)
    result = await db.execute(statement)
    # scalar_one_or_none: 결과가 하나면 그거 내놔, 없으면 none, 2개 이상은 에러
    return result.scalar_one_or_none()


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    """이메일로 유저를 조회합니다."""
    statement = select(User).where(User.email == email)
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def create_user(email: str, password: str, name: str, phone: str, role: str, address: str) -> dict:
    """유저를 생성합니다."""
    pass


async def authenticate_user(email: str, password: str) -> dict | None:
    """이메일과 비밀번호로 유저를 인증합니다."""
    pass
