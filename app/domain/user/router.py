"""유저 API 엔드포인트."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.database import get_db
from app.domain.user.dependency import get_current_user
from app.domain.user.models import User, UserRole
from app.domain.user.schemas import (
    DocumentCreateRequest,
    DocumentResponse,
    PasswordChangeRequest,
    RegisterResponse,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.domain.user.service import (
    authenticate_user,
    change_password,
    create_document,
    create_user,
    delete_document,
    get_document_by_id,
    get_documents_by_user_id,
    get_user_by_email,
)

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """회원가입 (유저 정보 + 토큰 반환 -> 가입 시 서류 업로드 때 토큰 필요)"""
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
    access_token = create_access_token({"sub": str(user.user_id)})
    return RegisterResponse(user=user, access_token=access_token)


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
    success = await change_password(
        current_user.user_id, body.current_password, body.new_password, db
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 올바르지 않습니다.",
        )


# ── 서류 ───────────────────
@router.post("/me/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    body: DocumentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """서류 업로드"""
    document = await create_document(
        user_id=current_user.user_id,
        document_type=body.document_type,
        document_url=str(body.document_url),  # Pydantic HttpUrl → str 변환 (DB 저장용)
        db=db,
    )
    return document


@router.get("/me/documents", response_model=list[DocumentResponse])
async def get_my_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """마이페이지: 내 서류 목록 조회"""
    return await get_documents_by_user_id(current_user.user_id, db)


# 204: 삭제 후 응답 바디가 없음(성공했지만 삭제라서 돌려줄 내용이 없음)
@router.delete("/me/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """서류 삭제"""
    document = await get_document_by_id(document_id, db)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="서류를 찾을 수 없습니다.",
        )
    if document.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 서류만 삭제할 수 있습니다.",
        )
    await delete_document(document_id, db)
