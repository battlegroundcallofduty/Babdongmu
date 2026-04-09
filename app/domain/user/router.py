"""유저 API 엔드포인트."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.database import get_db
from app.domain.user.dependency import get_current_user
from app.domain.user.models import User
from app.domain.user.schemas import (
    TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse)
from app.domain.user.service import (
    authenticate_user, create_user, get_user_by_email)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """회원가입을 처리합니다."""
    existing = await get_user_by_email(body.email, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일입니다.",)

    user = await create_user(
        email=body.email,
        password=body.password,
        name=body.name,
        phone_number=body.phone_number,
        user_role=body.user_role,
        address=body.address,
        db=db,
    )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """로그인을 처리합니다."""
    user = await authenticate_user(body.email, body.password, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": str(user.user_id)})
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """현재 로그인한 유저 정보를 반환합니다."""
    return current_user
