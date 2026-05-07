"""유저 요청/응답 스키마."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.domain.common.schemas import AddressCreate, AddressResponse
from app.domain.user.models import CertFlag, DocumentType, UserRole

# (요청: 클라이언트 -body(데이터)-> 서버)
# ── 유저 요청 ──────────────


class UserRegisterRequest(BaseModel):
    """회원가입 요청"""

    email: EmailStr
    password: str
    password_confirm: str  # 비밀번호 확인(라우터에서 안넘김)
    name: str = Field(min_length=1)
    phone_number: str = Field(min_length=1)
    user_role: UserRole  # volunteer | guardian
    address: AddressCreate

    @field_validator("password")  # 특정 필드(비번) 하나
    # userregisterrequest 객체가 없는 상태라서 클래스(cls) 받음
    @classmethod
    def password_min_length(cls, v):  # v: password 입력값
        if len(v) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다.")
        return v

    @model_validator(mode="after")  # 모델 전체(비번 - 비번확인 비교)
    # after: 모든 필드 처리 다 끝난 다음에 validator 실행 (self 가능)
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return self


class UserLoginRequest(BaseModel):
    """로그인 요청"""

    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    """회원정보 수정 요청 (마이페이지)"""

    address: AddressCreate | None = None


class PasswordChangeRequest(BaseModel):
    """비밀번호 변경 요청 (마이페이지)"""

    current_password: str
    new_password: str
    new_password_confirm: str

    @field_validator("new_password")
    @classmethod
    def new_password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다.")
        return v

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.new_password_confirm:
            raise ValueError("새 비밀번호가 일치하지 않습니다.")
        if self.current_password == self.new_password:
            raise ValueError("새 비밀번호가 현재 비밀번호와 같습니다.")
        return self


# ── 카카오 요청 ────────────────
class KakaoSetupRequest(BaseModel):
    """카카오 전용 회원가입 완료 요청"""

    setup_token: str
    name: str = Field(min_length=1)
    phone_number: str = Field(min_length=1)
    user_role: UserRole
    address: AddressCreate


# ── SMS 요청 ───────────────


class SmsSendRequest(BaseModel):
    """SMS 인증 코드 발송 요청"""

    phone_number: str = Field(min_length=1)


class SmsVerifyRequest(BaseModel):
    """SMS 인증 코드 확인 요청"""

    phone_number: str = Field(min_length=1)
    code: str = Field(min_length=6, max_length=6)


# ── 유저 응답 ─────────────────


class UserResponse(BaseModel):
    """유저 정보 반환 (비밀번호 제외)"""

    user_id: int
    email: str | None
    name: str
    phone_number: str | None
    user_role: UserRole
    address: AddressResponse
    cert_flag: CertFlag
    cert_reject_reason: str | None
    created_at: datetime
    is_social_login: bool

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """로그인 성공 시 토큰 반환"""

    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    """회원가입 성공 시 유저 정보 + 토큰 반환"""

    user: UserResponse
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


class DocumentUrlResponse(BaseModel):
    """서류 presigned URL 반환"""

    url: str
