"""Cloudflare R2 이미지 업로드 유틸리티."""

import enum
import logging
import uuid
# 로그 남길 수 있는 객체
logger = logging.getLogger(__name__)

import boto3
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, UploadFile

from app.config import settings

# 후기 이미지용(이미지만)
IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png"}

# 신원 서류용(이미지 + 문서 형식)
DOCUMENT_CONTENT_TYPES = {
    "image/jpeg",                # 브라우저가 서버에 보내는값(MIME 타입)
    "image/png",
    "application/pdf",
    "application/x-hwp",         # hwp: 브라우저마다 다른 유형 2개(MIME 타입 2종류)
    "application/haansoft-hwp",  # docx: 공식 유형, 한컴회사꺼 2개
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/haansoftdocx",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# 파일 형식이 늘어나서 딕셔너리로 변환
CONTENT_TYPE_EXT = {
    "image/jpeg": "jpg",         # R2에 저장할때 쓰는 확장자
    "image/png": "png",
    "application/pdf": "pdf",
    "application/x-hwp": "hwp",
    "application/haansoft-hwp": "hwp",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/haansoftdocx": "docx",
}


class BucketType(enum.Enum):
    PUBLIC = "public"    # 공개 버킷 (후기 이미지)
    PRIVATE = "private"  # 비공개 버킷 (신원 서류)


def _get_client() -> BaseClient:
    """R2 클라이언트를 반환합니다."""
    return boto3.client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


async def upload_image(
    file: UploadFile,
    folder: str,
    bucket: BucketType = BucketType.PUBLIC,
    allowed_types: set[str] | None = None,  # None이면 기본값 적용
) -> str:
    """이미지를 R2에 업로드하고 URL을 반환합니다.

    Args:
        file: 업로드할 이미지 파일
        folder: 저장할 폴더명 (예: "reviews", "documents")
        bucket: 버킷 유형 (BucketType.PUBLIC 또는 BucketType.PRIVATE)

    Returns:
        업로드된 이미지의 URL
    """
    # allowed_types 지정하면 지정한걸로 / 따로 지정안하면 기본: IMAGE_CONTENT_TYPES
    types = allowed_types if allowed_types is not None else IMAGE_CONTENT_TYPES
    if file.content_type not in types:
        raise HTTPException(status_code=400, detail="허용되지 않는 파일 형식입니다.")

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기는 최대 5MB까지 허용됩니다.")

    ext = CONTENT_TYPE_EXT.get(file.content_type, "bin")
    key = f"{folder}/{uuid.uuid4().hex}.{ext}"
    bucket_name = (
        settings.R2_PUBLIC_BUCKET if bucket == BucketType.PUBLIC else settings.R2_PRIVATE_BUCKET
    )

    try:
        client = _get_client()
        client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=contents,
            ContentType=file.content_type,
        )
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=503, detail=f"이미지 업로드에 실패했습니다. {e}")

    # 공개 버킷은 CDN URL, 비공개 버킷은 엔드포인트 URL 반환
    if bucket == BucketType.PUBLIC:
        return f"{settings.R2_PUBLIC_URL}/{key}"
    return f"{settings.R2_ENDPOINT}/{bucket_name}/{key}"


async def delete_image(image_url: str) -> None:
    """R2에서 이미지를 삭제합니다.

    Args:
        image_url: 삭제할 이미지의 URL
    """
    # 공개/비공개 버킷 판별 후 key 추출
    if image_url.startswith(settings.R2_PUBLIC_URL):
        bucket = settings.R2_PUBLIC_BUCKET
        key = image_url[len(settings.R2_PUBLIC_URL) + 1:]
    else:
        bucket = settings.R2_PRIVATE_BUCKET
        prefix = f"{settings.R2_ENDPOINT}/{bucket}/"
        if not image_url.startswith(prefix):
            return
        key = image_url[len(prefix):]

    try:
        client = _get_client()
        client.delete_object(Bucket=bucket, Key=key)
    except (BotoCoreError, ClientError) as e:
        # 삭제 실패해도 DB 삭제는 진행하되 로그 남김 (R2 고아 파일 추적용)
        logger.error("R2 파일 삭제 실패 url=%s error=%s", image_url, e)
