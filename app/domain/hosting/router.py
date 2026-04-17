"""호스팅 API 라우터."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.hosting.schema import HostingCreateRequest, HostingResponse
from app.domain.hosting.service import (
    cancel_hosting,
    create_hosting,
    get_hosting_detail,
    list_hostings_by_guardian,
)
from app.domain.user.dependency import require_guardian


router = APIRouter()


@router.post(
    "/",
    response_model=HostingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_hosting_endpoint(
    request: HostingCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_guardian=Depends(require_guardian),
) -> HostingResponse:
    """호스팅을 등록합니다."""

    return await create_hosting(
        session=session,
        guardian_id=current_guardian.user_id,
        request=request,
    )


@router.get(
    "/",
    response_model=list[HostingResponse],
    status_code=status.HTTP_200_OK,
)
async def list_hostings_endpoint(
    session: AsyncSession = Depends(get_db),
    current_guardian=Depends(require_guardian),
) -> list[HostingResponse]:
    """보호자의 호스팅 목록을 조회합니다."""

    return await list_hostings_by_guardian(
        session=session,
        guardian_id=current_guardian.user_id,
    )


@router.get(
    "/{hosting_id}",
    response_model=HostingResponse,
    status_code=status.HTTP_200_OK,
)
async def get_hosting_detail_endpoint(
    hosting_id: int,
    session: AsyncSession = Depends(get_db),
    current_guardian=Depends(require_guardian),
) -> HostingResponse:
    """보호자의 호스팅 상세 정보를 조회합니다."""

    return await get_hosting_detail(
        session=session,
        guardian_id=current_guardian.user_id,
        hosting_id=hosting_id,
    )


@router.patch(
    "/{hosting_id}/cancel",
    response_model=HostingResponse,
    status_code=status.HTTP_200_OK,
)
async def cancel_hosting_endpoint(
    hosting_id: int,
    session: AsyncSession = Depends(get_db),
    current_guardian=Depends(require_guardian),
) -> HostingResponse:
    """호스팅을 무산 처리합니다."""

    return await cancel_hosting(
        session=session,
        guardian_id=current_guardian.user_id,
        hosting_id=hosting_id,
    )