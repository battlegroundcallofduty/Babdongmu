"""유저 API 엔드포인트."""

from fastapi import APIRouter, HTTPException

from app.domain.user.schema import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest) -> TokenResponse:
    """회원가입을 처리합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> TokenResponse:
    """로그인을 처리합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.get("/me", response_model=UserResponse)
async def get_me() -> UserResponse:
    """현재 로그인한 유저 정보를 반환합니다."""
    raise HTTPException(status_code=501, detail="미구현")
