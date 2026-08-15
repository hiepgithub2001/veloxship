"""AWS S3 client factory (via aioboto3)."""
from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from pathlib import PurePosixPath

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
