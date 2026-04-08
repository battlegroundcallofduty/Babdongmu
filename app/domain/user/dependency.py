"""유저 인증 의존성."""

from fastapi import Depends, HTTPException
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
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    user = await get_user_by_id(int(user_id), db)
    if user is None:
        raise HTTPException(status_code=401, detail="유저를 찾을 수 없습니다.")

    return user
