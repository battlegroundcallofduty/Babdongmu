"""유저 API 엔드포인트."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.database import get_db
from app.domain.user.dependency import get_current_user
from app.domain.user.models import User, UserRole
from app.domain.user.schemas import (
    PasswordChangeRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.domain.user.service import authenticate_user, change_password, create_user, get_user_by_email

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """회원가입"""
    # admin 역할로는 가입 불가 — admin은 seed 스크립트로 별도 생성
    if body.user_role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 역할입니다.",
        )

    existing = await get_user_by_email(body.email, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일입니다.",
        )

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
    """로그인"""
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
    """현재 로그인한 유저 정보 반환"""
    return current_user  # orm 객체: db 테이블의 한 행을 python 객체로 감싼것


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(
    body: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """마이페이지: 비밀번호 변경"""
    if current_user.password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="소셜 로그인 계정은 비밀번호를 변경할 수 없습니다.",
        )
    success = await change_password(current_user.user_id, body.current_password, body.new_password, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 올바르지 않습니다.",
        )
