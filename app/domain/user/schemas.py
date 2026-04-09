"""유저 요청/응답 스키마."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


# == 요청 스키마

class UserRegisterRequest(BaseModel):
    """회원가입 요청"""
    email: EmailStr
    password: str
    name: str
    phone_number: str
    user_role: str  # volunteer | guardian
    address: str


class UserLoginRequest(BaseModel):
    """로그인 요청"""
    email: EmailStr
    password: str


# == 응답 스키마

class UserResponse(BaseModel):
    """유저 정보 반환 (비밀번호 제외)"""
    user_id: int
    email: str
    name: str
    phone_number: str
    user_role: str
    address: str
    cert_flag: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """로그인 성공 시 토큰 반환"""
    access_token: str
    token_type: str = "bearer"
