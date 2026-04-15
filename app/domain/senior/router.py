"""어르신 API 라우터."""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.senior.schema import (
    SeniorCreateRequest,
    SeniorResponse,
    SeniorUpdateRequest,
)
from app.domain.senior.service import (
    activate_senior,
    create_senior,
    deactivate_senior,
    delete_senior,
    get_guardian_senior_by_id,
    list_seniors_by_guardian,
    update_senior,
)
from app.domain.user.dependency import get_current_guardian


router = APIRouter()


@router.post(
    "/",
    response_model=SeniorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_senior_endpoint(
    request: SeniorCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_guardian=Depends(get_current_guardian),
) -> SeniorResponse:
    """어르신을 등록합니다."""

    return await create_senior(
        session=session,
        guardian_id=current_guardian.user_id,
        request=request,
    )


@router.get(
    "/",
    response_model=list[SeniorResponse],
    status_code=status.HTTP_200_OK,
)
async def list_seniors_endpoint(
    session: AsyncSession = Depends(get_db),
    current_guardian=Depends(get_current_guardian),
) -> list[SeniorResponse]:
    """보호자의 어르신 목록을 조회합니다."""

    return await list_seniors_by_guardian(
        session=session,
        guardian_id=current_guardian.user_id,
    )


@router.get(
    "/{senior_id}",
    response_model=SeniorResponse,
    status_code=status.HTTP_200_OK,
)
async def get_senior_detail_endpoint(
    senior_id: int,
    session: AsyncSession = Depends(get_db),
    current_guardian=Depends(get_current_guardian),
) -> SeniorResponse:
    """보호자의 어르신 상세 정보를 조회합니다."""

    senior = await get_guardian_senior_by_id(
        session=session,
        guardian_id=current_guardian.user_id,
        senior_id=senior_id,
    )
    return SeniorResponse.model_validate(senior)


@router.patch(
    "/{senior_id}",
    response_model=SeniorResponse,
    status_code=status.HTTP_200_OK,
)
async def update_senior_endpoint(
    senior_id: int,
    request: SeniorUpdateRequest,
    session: AsyncSession = Depends(get_db),
    current_guardian=Depends(get_current_guardian),
) -> SeniorResponse:
    """어르신 정보를 수정합니다."""

    return await update_senior(
        session=session,
        guardian_id=current_guardian.user_id,
        senior_id=senior_id,
        request=request,
    )


@router.patch(
    "/{senior_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_senior_endpoint(
    senior_id: int,
    session: AsyncSession = Depends(get_db),
    current_guardian=Depends(get_current_guardian),
) -> Response:
    """어르신 정보를 비활성화합니다."""

    await deactivate_senior(
        session=session,
        guardian_id=current_guardian.user_id,
        senior_id=senior_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{senior_id}/activate",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def activate_senior_endpoint(
    senior_id: int,
    session: AsyncSession = Depends(get_db),
    current_guardian=Depends(get_current_guardian),
) -> Response:
    """어르신 정보를 활성화합니다."""

    await activate_senior(
        session=session,
        guardian_id=current_guardian.user_id,
        senior_id=senior_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/{senior_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_senior_endpoint(
    senior_id: int,
    session: AsyncSession = Depends(get_db),
    current_guardian=Depends(get_current_guardian),
) -> Response:
    """어르신 정보를 삭제합니다."""

    await delete_senior(
        session=session,
        guardian_id=current_guardian.user_id,
        senior_id=senior_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)