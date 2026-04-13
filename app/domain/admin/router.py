"""관리자 API 엔드포인트."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.hosting.models import Hosting
from app.domain.match.models import MatchingInfo
from app.domain.senior.models import Senior
from app.domain.user.dependency import require_admin
from app.domain.user.models import CertFlag, Document, User, UserRole

router = APIRouter()


# ── 통계 ──────────────────────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    """대시보드 통계를 반환합니다."""
    doc_pending = await db.scalar(
        select(func.count()).select_from(Document)
        .join(User, Document.user_id == User.user_id)
        .where(User.cert_flag == CertFlag.PENDING)
    )
    approved_volunteers = await db.scalar(
        select(func.count()).select_from(User)
        .where(User.user_role == UserRole.VOLUNTEER, User.cert_flag == CertFlag.APPROVED)
    )
    total_volunteers = await db.scalar(
        select(func.count()).select_from(User)
        .where(User.user_role == UserRole.VOLUNTEER)
    )
    seniors = await db.scalar(
        select(func.count()).select_from(Senior)
        .where(Senior.active_flag.is_(True))
    )
    time_pending = await db.scalar(
        select(func.count()).select_from(MatchingInfo)
        .where(MatchingInfo.check_out_time.is_not(None), MatchingInfo.actual_volunteer_time.is_(None))
    )
    today = datetime.now(timezone.utc).date()
    today_matches = await db.scalar(
        select(func.count()).select_from(MatchingInfo)
        .where(func.date(MatchingInfo.created_at) == today)
    )

    return {
        "doc_pending": doc_pending,
        "approved_volunteers": approved_volunteers,
        "total_volunteers": total_volunteers,
        "seniors": seniors,
        "time_pending": time_pending,
        "today_matches": today_matches,
    }


# ── 서류 승인/반려 ──────────────────────────────────────────────────────────────

@router.get("/documents/pending")
async def list_pending_documents(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[dict]:
    """승인 대기 중인 봉사자 서류 목록을 반환합니다."""
    result = await db.execute(
        select(Document, User)
        .join(User, Document.user_id == User.user_id)
        .where(User.cert_flag == CertFlag.PENDING)
        .order_by(Document.created_at.asc())
    )
    rows = result.all()

    return [
        {
            "document_id": doc.document_id,
            "user_id": user.user_id,
            "user_name": user.name,
            "user_email": user.email,
            "document_type": doc.document_type,
            "document_url": doc.document_url,
            "created_at": doc.created_at.isoformat(),
        }
        for doc, user in rows
    ]


@router.patch("/documents/{document_id}/approve", status_code=status.HTTP_200_OK)
async def approve_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    """서류를 승인하고 cert_flag를 approved로 변경합니다."""
    doc_result = await db.execute(select(Document).where(Document.document_id == document_id))
    doc = doc_result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="서류를 찾을 수 없습니다.")

    user_result = await db.execute(select(User).where(User.user_id == doc.user_id))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="유저를 찾을 수 없습니다.")

    user.cert_flag = CertFlag.APPROVED
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return {"user_id": user.user_id, "cert_flag": user.cert_flag}


@router.patch("/documents/{document_id}/reject", status_code=status.HTTP_200_OK)
async def reject_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    """서류를 반려하고 cert_flag를 rejected로 변경합니다."""
    doc_result = await db.execute(select(Document).where(Document.document_id == document_id))
    doc = doc_result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="서류를 찾을 수 없습니다.")

    user_result = await db.execute(select(User).where(User.user_id == doc.user_id))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="유저를 찾을 수 없습니다.")

    user.cert_flag = CertFlag.REJECTED
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return {"user_id": user.user_id, "cert_flag": user.cert_flag}


# ── 최근 매칭 신청 ────────────────────────────────────────────────────────────

@router.get("/matches/recent")
async def list_recent_matches(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
    limit: int = 5,
) -> list[dict]:
    """최근 매칭 신청 목록을 반환합니다."""
    result = await db.execute(
        select(MatchingInfo, User, Hosting, Senior)
        .join(User, MatchingInfo.vt_id == User.user_id)
        .join(Hosting, MatchingInfo.hosting_id == Hosting.hosting_id)
        .join(Senior, Hosting.senior_id == Senior.senior_id)
        .order_by(MatchingInfo.created_at.desc())
        .limit(limit)
    )
    rows = result.all()
    return [
        {
            "matching_id": m.matching_id,
            "volunteer_name": u.name,
            "senior_name": s.name,
            "hosting_at": h.hosting_at.isoformat(),
            "match_status": m.match_status.value,
            "created_at": m.created_at.isoformat(),
        }
        for m, u, h, s in rows
    ]


# ── 봉사시간 부여 ──────────────────────────────────────────────────────────────
class VolunteerTimeRequest(BaseModel):
    actual_volunteer_time: int  # 분 단위


@router.get("/matches/completed")
async def list_completed_matches(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[dict]:
    """체크아웃 완료 후 봉사시간 미부여 매칭 목록을 반환합니다.
    """
    result = await db.execute(
        select(MatchingInfo, User, Hosting, Senior)
        .join(User, MatchingInfo.vt_id == User.user_id)
        .join(Hosting, MatchingInfo.hosting_id == Hosting.hosting_id)
        .join(Senior, Hosting.senior_id == Senior.senior_id)
        .where(
            MatchingInfo.check_out_time.is_not(None),
            MatchingInfo.actual_volunteer_time.is_(None),
        )
        .order_by(MatchingInfo.check_out_time.asc())
    )
    rows = result.all()
    return [
        {
            "matching_id": m.matching_id,
            "volunteer_name": u.name,
            "senior_name": s.name,
            "check_in_time": m.check_in_time.isoformat() if m.check_in_time else None,
            "check_out_time": m.check_out_time.isoformat(),
            "expected_minutes": int((h.hosting_end - h.hosting_at).total_seconds() // 60) if h.hosting_end else None,
        }
        for m, u, h, s in rows
    ]


@router.patch("/matches/{matching_id}/volunteer-time", status_code=status.HTTP_200_OK)
async def grant_volunteer_time(
    matching_id: int,
    payload: VolunteerTimeRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    """봉사시간을 최종 부여합니다.

    민지님의 MatchingInfo 확장 후 활성화 예정.
    """

    result = await db.execute(select(MatchingInfo).where(MatchingInfo.matching_id == matching_id))
    match = result.scalar_one_or_none()
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="매칭을 찾을 수 없습니다.")
    match.actual_volunteer_time = payload.actual_volunteer_time
    await db.commit()
    return {"matching_id": matching_id, "actual_volunteer_time": payload.actual_volunteer_time}
