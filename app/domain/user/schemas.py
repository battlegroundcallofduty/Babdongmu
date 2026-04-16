"""유저 요청/응답 스키마."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, HttpUrl, field_validator, model_validator

from app.domain.user.models import CertFlag, DocumentType, UserRole


# (요청: 클라이언트가 서버에 body로 데이터를 보낼때)
# ── 유저 요청 ──────────────

class UserRegisterRequest(BaseModel):
    """회원가입 요청"""

    email: EmailStr
    password: str
    password_confirm: str  # 비밀번호 확인(라우터에서 넘길필요없음~)
    name: str
    phone_number: str
    user_role: UserRole    # volunteer | guardian
    address: str

    @field_validator("password") # 특정 필드 하나
    # 비번 필드 하나만 들어왔을때 실행되서 userregisterrequest 객체가 없는 상태
    @classmethod # 그래서 self 객체 대신 클래스를 받는다(cls)
    def password_min_length(cls, v): # v: password 입력값
        if len(v) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다.")
        return v
    
    @model_validator(mode="after") # 모델 전체(비번, 비번확인 비교)
    # mode="after": 모든 필드 처리 다 끝난 다음에 validator 실행 (self 가능)
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

    name: str | None = None
    phone_number: str | None = None
    address: str | None = None


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
        return self


# ── 서류 요청 ────────────────

class DocumentCreateRequest(BaseModel):
    """서류 업로드 요청"""

    document_type: DocumentType
    # HttpUrl로 스킴/형식 검증 (javascript:, data: 등 차단). 렌더링 시 textContent 사용 권장
    document_url: HttpUrl


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
    is_social_login: bool

    # sqlalchemy orm 객체를 pydantic 스키마로 변환할때 객체 속성 읽게해줌
    # 이 설정 때문에 @property도 읽을수있음
    model_config = {"from_attributes": True}



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
