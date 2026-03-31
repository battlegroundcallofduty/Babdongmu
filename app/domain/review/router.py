"""후기 API 엔드포인트."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("")
async def create_review():
    """후기를 작성합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.get("/senior/{senior_id}")
async def list_reviews_by_senior(senior_id: str):
    """어르신별 후기를 조회합니다."""
    raise HTTPException(status_code=501, detail="미구현")
