"""유저 API 엔드포인트."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/register")
async def register():
    """회원가입을 처리합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.post("/login")
async def login():
    """로그인을 처리합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.get("/me")
async def get_me():
    """현재 로그인한 유저 정보를 반환합니다."""
    raise HTTPException(status_code=501, detail="미구현")
