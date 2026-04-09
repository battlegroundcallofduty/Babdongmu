"""유저 인증 의존성."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database import get_db
from app.domain.user.models import User
from app.domain.user.service import get_user_by_id

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """JWT 토큰에서 현재 유저를 추출합니다."""

    # 401 에러시 공통으로 반환하는 예외 객체
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 토큰입니다.",
        headers={"WWW-Authenticate": "Bearer"},  # 인증 실패라고 헤더에 알려주는거
    )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # sub 값을 정수로 방어도 해주고, 정수가 아닌 경우 500 에러 말고 401 에러로
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
