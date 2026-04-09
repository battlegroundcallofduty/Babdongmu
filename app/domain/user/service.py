"""유저 비즈니스 로직."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.domain.user.models import User, UserRole


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


async def create_user(
    email: str,
    password: str,
    name: str,
    phone_number: str,
    user_role: UserRole,
    address: str,
    db: AsyncSession,
) -> User:
    """회원가입: 유저를 생성합니다."""
    user = User(
        email=email,
        password=hash_password(password),
        name=name,
        phone_number=phone_number,
        user_role=user_role,
        address=address,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(email: str, password: str, db: AsyncSession) -> User | None:
    """로그인: 이메일과 비밀번호로 유저를 인증합니다. 실패 시 None 반환."""
    user = await get_user_by_email(email, db)
    if user is None:
        return None
    if not verify_password(password, user.password):
        return None
    return user
