"""유저 인증 의존성."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database import get_db
from app.domain.user.models import User, UserRole
from app.domain.user.service import get_user_by_id

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """JWT 토큰에서 현재 유저 추출"""

    # 401 에러시 공통으로 반환하는 예외 객체
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 토큰입니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # sub 값을 정수로 방어, 정수가 아닌 경우: 401 에러
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise credentials_exception

    user = await get_user_by_id(user_id_int, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유저를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """관리자 권한 확인(관리자만 접근 가능)"""
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 접근할 수 있습니다.",
        )
    return current_user


async def require_guardian(current_user: User = Depends(get_current_user)) -> User:
    """보호자 권한 확인(보호자만 접근 가능)"""
    if current_user.user_role != UserRole.GUARDIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="보호자만 접근할 수 있습니다.",
        )
    return current_user


async def require_volunteer(current_user: User = Depends(get_current_user)) -> User:
    """봉사자 권한 확인(봉사자만 접근 가능)"""
    if current_user.user_role != UserRole.VOLUNTEER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="봉사자만 접근할 수 있습니다.",
        )
    return current_user


async def require_approved_volunteer(
    current_volunteer=Depends(require_volunteer),
):
    """승인된 봉사자만 통과시킵니다."""

    if getattr(current_volunteer, "cert_flag", None) != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="승인된 봉사자만 호스팅을 탐색할 수 있습니다.",
        )

    return current_volunteer