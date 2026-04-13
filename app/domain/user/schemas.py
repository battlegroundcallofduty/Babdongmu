"""유저 요청/응답 스키마."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.domain.user.models import CertFlag, DocumentType, UserRole


# (요청: 클라이언트가 서버에 body로 데이터를 보낼때)
# ── 유저 요청 ──────────────

class UserRegisterRequest(BaseModel):
    """회원가입 요청"""

    email: EmailStr
    password: str
    name: str
    phone_number: str
    user_role: UserRole  # volunteer | guardian
    address: str


class UserLoginRequest(BaseModel):
    """로그인 요청"""

    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    """회원정보 수정 요청 (마이페이지)"""

    name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None


# ── 서류 요청 ────────────────

class DocumentCreateRequest(BaseModel):
    """서류 업로드 요청"""

    document_type: DocumentType
    document_url: str


class DocumentUpdateRequest(BaseModel):
    """서류 수정 요청"""

    document_url: str


# ── SMS 요청 ───────────────

class SmsSendRequest(BaseModel):
    """SMS 인증 코드 발송 요청"""

    phone_number: str


class SmsVerifyRequest(BaseModel):
    """SMS 인증 코드 확인 요청"""

    phone_number: str
    code: str


# ── 유저 응답 ─────────────────

class UserResponse(BaseModel):
    """유저 정보 반환 (비밀번호 제외)"""

    user_id: int
    email: str
    name: str
    phone_number: str
    user_role: UserRole
    address: str
    cert_flag: CertFlag
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """로그인 성공 시 토큰 반환"""

    access_token: str
    token_type: str = "bearer"


# ── 서류 응답 ────────────────────

class DocumentResponse(BaseModel):
    """서류 정보 반환"""

    document_id: int
    user_id: int
    document_type: DocumentType
    document_url: str
    created_at: datetime

    model_config = {"from_attributes": True}
