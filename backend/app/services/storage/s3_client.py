"""AWS S3 client factory (via aioboto3)."""
from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

import aioboto3
import boto3

from app.core.config import settings


def build_object_key(prefix: str, safe_filename: str, ext: str) -> str:
    ts_id = uuid.uuid4().hex[:12]
    return str(PurePosixPath(prefix) / f"{ts_id}_{safe_filename}")


def generate_presigned_url(key: str, expires_in: int | None = None) -> str:
    """Generate a presigned GET URL for an S3 object key. Fast local signing (0 network calls)."""
    if not key or not isinstance(key, str) or not key.strip():
        return ""
    if key.startswith("http://") or key.startswith("https://") or key.startswith("blob:"):
        return key

    if expires_in is None:
        expires_in = settings.S3_PRESIGNED_URL_EXPIRES_IN

    client = boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET_NAME, "Key": key},
        ExpiresIn=expires_in,
    )


def extract_key_from_presigned_url(url: str) -> str | None:
    """Reverse of ``generate_presigned_url``: recover the S3 object key from one of
    our own presigned URLs, so round-tripped HTML can store keys (not expiring URLs).

    Returns ``None`` when ``url`` is not a presigned URL of this bucket (e.g. an
    external image URL or a bare object key), leaving the caller to keep it as-is.
    """
    if not url or not isinstance(url, str):
        return None
    if not (url.startswith("http://") or url.startswith("https://")):
        return None

    parsed = urlparse(url)
    host = parsed.netloc.lower()
    bucket = settings.S3_BUCKET_NAME
    path = unquote(parsed.path).lstrip("/")
    if not path or not bucket:
        return None

    # virtual-hosted style: {bucket}.s3.{region}.amazonaws.com/{key}
    if host.startswith(f"{bucket.lower()}."):
        return path
    # path-style: s3.{region}.amazonaws.com/{bucket}/{key}
    if host.endswith("amazonaws.com") and path.lower().startswith(f"{bucket.lower()}/"):
        return path[len(bucket) + 1 :]
    return None


@asynccontextmanager
async def get_s3_client():
    session = aioboto3.Session()
    kwargs = {
        "service_name": "s3",
        "region_name": settings.AWS_REGION,
        "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
    }

    async with session.client(**kwargs) as client:
        yield client
