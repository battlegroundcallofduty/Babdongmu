"""유저 요청/응답 DTO."""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """회원가입 요청."""

    email: EmailStr
    password: str
    name: str
    phone: str
    role: str  # "volunteer" | "guardian" | "admin"
    district: str


class LoginRequest(BaseModel):
    """로그인 요청."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """토큰 응답."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """유저 정보 응답."""

    id: str
    email: str
    name: str
    phone: str
    role: str
    district: str
