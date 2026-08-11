"""Upload a validated file to AWS S3 via aioboto3."""
from __future__ import annotations

import uuid
from pathlib import PurePosixPath

from app.core.config import settings
from app.services.storage.s3_client import get_s3_client


def build_object_key(prefix: str, safe_filename: str, ext: str) -> str:
    ts_id = uuid.uuid4().hex[:12]
    return str(PurePosixPath(prefix) / f"{ts_id}_{safe_filename}")


def build_public_url(key: str) -> str | None:
    if not settings.S3_PUBLIC_BASE_URL:
        return None
    return f"{settings.S3_PUBLIC_BASE_URL.rstrip('/')}/{key}"


async def upload_to_s3(*, file_obj, key: str, content_type: str, size_bytes: int) -> None:
    async with get_s3_client() as s3:
        await s3.upload_fileobj(
            Fileobj=file_obj,
            Bucket=settings.S3_BUCKET_NAME,
            Key=key,
            ExtraArgs={
                "ContentType": content_type,
                "ContentLength": size_bytes,
            },
        )
