"""유저 비즈니스 로직."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.domain.user.models import Document, User, UserRole

ALLOWED_UPDATE_FIELDS = {"name", "phone_number", "address"} # update_user 허용 리스트


# —— 유저 ─────────
async def get_user_by_id(user_id: int, db: AsyncSession) -> User | None:
    """ID로 유저 조회"""
    # 유저 가져올때 서류 정보 가져와야 하면 추후 selectinload 추가될듯
    statement = select(User).where(User.user_id == user_id)
    result = await db.execute(statement)
    # scalar_one_or_none: 결과가 하나면 그거 내놔, 없으면 none, 2개 이상은 에러
    return result.scalar_one_or_none()


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    """이메일로 유저 조회"""
    statement = select(User).where(User.email == email)
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def create_user(email: str, password: str, name: str,
    phone_number: str, user_role: UserRole, address: str, db: AsyncSession,) -> User:
    """회원가입: 유저 생성"""
    user = User(
        email=email,
        password=hash_password(password),
        name=name,
        phone_number=phone_number,
        user_role=user_role,
        address=address,)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(email: str, password: str, db: AsyncSession) -> User | None:
    """로그인: 이메일과 비밀번호로 유저 인증. 실패 시 None 반환."""
    user = await get_user_by_email(email, db)
    if user is None:
        return None
    # 카카오 함수 만들면 비밀번호 관련 방어 추가해야함
    if not verify_password(password, user.password):
        return None
    return user


# **kwargs: 가변적으로 받는 딕셔너리
async def update_user(user_id: int, db: AsyncSession, **kwargs) -> User | None:
    """마이페이지: 회원정보 수정"""
    user = await get_user_by_id(user_id, db)
    if user is None:
        return None
    for field, value in kwargs.items():
        if field not in ALLOWED_UPDATE_FIELDS:
            continue  # setattr 실행 안 하고 다음 필드로
        setattr(user, field, value) # 들어온것 업데이트
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)
    return user


async def change_password(user_id: int, current_password: str, new_password: str, db: AsyncSession) -> bool:
    """마이페이지: 비밀번호 변경 (불일치 에러는 router.py에서)"""
    user = await get_user_by_id(user_id, db)
    if user is None:
        return False  # 원래는 404 에러 직접 던지는게 맞지만 service는 순수 파이썬 영역으로 두기 위해 ^^
    if user.password is None:
        return False
    if not verify_password(current_password, user.password):
        # 현재 비밀번호가 틀리면 변경 거부
        return False
    user.password = hash_password(new_password)  # 해싱(security.py)
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return True


async def delete_user(user_id: int, db: AsyncSession) -> None:
    """탈퇴: 유저를 db에서 삭제"""
    user = await get_user_by_id(user_id, db)
    if user is None:
        return # 여기서 함수 종료하라는 뜻(return None과 같음)
    await db.delete(user)
    await db.commit()


# ── 서류 ───────────
async def get_document_by_id(document_id: int, db: AsyncSession) -> Document | None:
    """document_id(PK)에 해당되는 서류 조회"""
    statement = select(Document).where(Document.document_id == document_id)
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def get_documents_by_user_id(user_id: int, db: AsyncSession) -> list[Document]:
    """마이페이지: 유저의 서류 목록 조회"""
    statement = select(Document).where(Document.user_id == user_id)
    result = await db.execute(statement)
    return list(result.scalars().all())  # 유저당 서류는 여러개니깐/ 결과 없으면 빈 리스트 반환


async def create_document(user_id: int, document_type: str, document_url: str, db: AsyncSession) -> Document:
    """서류 업로드"""
    pass


async def update_document(document_id: int, document_url: str, db: AsyncSession) -> Document | None:
    """서류 수정"""
    pass


async def delete_document(document_id: int, db: AsyncSession) -> None:
    """서류 삭제"""
    pass


# ── 카카오 ─────────
async def get_or_create_kakao_user(kakao_id: str, email: str, name: str, db: AsyncSession) -> User:
    """카카오 로그인/회원가입 통합: kakao_id로 유저를 조회하고, 없으면 생성"""
    pass


# ── SMS 인증 ────────
async def send_phone_verification(phone_number: str, db: AsyncSession) -> None:
    """SMS 인증 코드 생성하고 발송"""
    pass


async def verify_phone_code(phone_number: str, code: str, db: AsyncSession) -> bool:
    """SMS 인증 코드 확인. 성공 시 True 반환."""
    pass
