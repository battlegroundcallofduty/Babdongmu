"""후기 API 엔드포인트."""

from fastapi import APIRouter, HTTPException

from app.domain.review.schema import ReviewCreateRequest, ReviewResponse

router = APIRouter()


@router.post("", response_model=ReviewResponse)
async def create_review(request: ReviewCreateRequest) -> ReviewResponse:
    """후기를 작성합니다."""
    raise HTTPException(status_code=501, detail="미구현")


@router.get("/senior/{senior_id}", response_model=list[ReviewResponse])
async def list_reviews_by_senior(senior_id: str) -> list[ReviewResponse]:
    """어르신별 후기를 조회합니다."""
    raise HTTPException(status_code=501, detail="미구현")
