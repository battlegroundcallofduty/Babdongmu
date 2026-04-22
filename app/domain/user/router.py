"""유저 API 엔드포인트."""

import asyncio

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.database import get_db
from app.domain.senior.service import list_seniors_by_guardian
from app.domain.user.dependency import get_current_user
from app.domain.user.models import DocumentType, User, UserRole
from app.domain.user.schemas import (
    DocumentResponse,
    PasswordChangeRequest,
    RegisterResponse,
    SmsSendRequest,
    SmsVerifyRequest,
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
    delete_user,
    get_document_by_id,
    get_documents_by_user_id,
    get_user_by_email,
    delete_phone_verifications,
    send_phone_verification,
    verify_phone_code,
)
from app.services.r2 import (
    DOCUMENT_CONTENT_TYPES,
    BucketType,
    delete_image,
    get_presigned_url,
    upload_image,
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
    await delete_phone_verifications(body.phone_number, db)
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
    return current_user


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


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """회원 탈퇴"""
    # 보호자인 경우 등록된 어르신이 있으면 탈퇴 차단
    if current_user.user_role == UserRole.GUARDIAN:  # 비활성 포함 전체 조회
        seniors = await list_seniors_by_guardian(db, current_user.user_id, active_only=False)
        if seniors:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="등록된 어르신이 있어 탈퇴할 수 없습니다. 먼저 어르신 정보를 삭제해주세요.",
            )
    # R2 파일 먼저 삭제 (유저 삭제 후 CASCADE로 DB는 사라지지만 R2 파일은 안 사라짐)
    documents = await get_documents_by_user_id(current_user.user_id, db)
    await asyncio.gather(
        *[delete_image(doc.document_url) for doc in documents], return_exceptions=True
    )
    await delete_user(current_user.user_id, db)


# ── 서류 ───────────────────
@router.post("/me/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    document_type: DocumentType = Form(...),  # 텍스트 조각(서류유형)
    file: UploadFile = File(...),  # 파일 조각(실제 파일 바이너리)
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """서류 업로드 (파일 → R2 업로드 → DB 저장)"""
    # 1) 파일 R2 private 버킷에 올리고 URL 받기
    document_url = await upload_image(
        file, folder="documents", bucket=BucketType.PRIVATE, allowed_types=DOCUMENT_CONTENT_TYPES
    )
    # 2) URL을 db에 저장
    document = await create_document(
        user_id=current_user.user_id,
        document_type=document_type,
        document_url=document_url,
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

# 204: 삭제 후 응답 바디 X(성공했지만 돌려줄 내용 x)
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
    await delete_image(document.document_url)  # R2 파일 먼저 삭제
    await delete_document(document_id, db)

@router.get("/documents/{document_id}/presigned-url")
async def get_document_url(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """서류 presigned URL 반환 (본인 서류 또는 관리자만 접근 가능, 5분 유효)."""
    document = await get_document_by_id(document_id, db)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="서류를 찾을 수 없습니다."
        )
    if current_user.user_role != UserRole.ADMIN and document.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다."
        )
    return {"url": get_presigned_url(document.document_url)}


# ── SMS 인증 ───────────────────
@router.post("/phone/send", status_code=status.HTTP_204_NO_CONTENT)
async def send_verification(body: SmsSendRequest, db: AsyncSession = Depends(get_db)):
    """SMS 인증 코드 발송"""
    success = await send_phone_verification(body.phone_number, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SMS 발송에 실패했습니다. 잠시 후 다시 시도해주세요.",
        )


@router.post("/phone/verify", status_code=status.HTTP_204_NO_CONTENT)
async def verify_verification(body: SmsVerifyRequest, db: AsyncSession = Depends(get_db)):
    """SMS 인증 번호 확인"""
    result = await verify_phone_code(body.phone_number, body.code, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인증 번호가 만료되었습니다. 다시 요청해주세요.",
        )
    if result is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인증 번호가 일치하지 않습니다.",
        )
# TODO: service 또는 router에 가입 전 동일번호 존재여부 조회후 409 반환예정 / 폰번 unique 고려
