"""Cloudflare R2 이미지 업로드 유틸리티."""

import uuid

import boto3
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, UploadFile

from app.config import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def _get_client() -> BaseClient:
    """R2 클라이언트를 반환합니다."""
    return boto3.client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


async def upload_image(file: UploadFile, folder: str) -> str:
    """이미지를 R2에 업로드하고 URL을 반환합니다.

    Args:
        file: 업로드할 이미지 파일
        folder: 저장할 폴더명 (예: "reviews", "documents")

    Returns:
        업로드된 이미지의 URL
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="jpg, png 파일만 업로드할 수 있습니다.")

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기는 최대 5MB까지 허용됩니다.")

    ext = "jpg" if file.content_type == "image/jpeg" else "png"
    key = f"{folder}/{uuid.uuid4().hex}.{ext}"

    try:
        client = _get_client()
        client.put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=key,
            Body=contents,
            ContentType=file.content_type,
        )
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=503, detail=f"이미지 업로드에 실패했습니다. {e}")

    return f"{settings.R2_ENDPOINT}/{settings.R2_BUCKET_NAME}/{key}"


async def delete_image(image_url: str) -> None:
    """R2에서 이미지를 삭제합니다.

    Args:
        image_url: 삭제할 이미지의 URL
    """
    # URL에서 key 추출 (endpoint/bucket/key 형태)
    prefix = f"{settings.R2_ENDPOINT}/{settings.R2_BUCKET_NAME}/"
    if not image_url.startswith(prefix):
        return
    key = image_url[len(prefix):]

    try:
        client = _get_client()
        client.delete_object(Bucket=settings.R2_BUCKET_NAME, Key=key)
    except (BotoCoreError, ClientError):
        pass  # R2 삭제 실패해도 DB 삭제는 진행
