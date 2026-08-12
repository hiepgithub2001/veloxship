"""AWS S3 client factory (via aioboto3)."""
from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from pathlib import PurePosixPath

import aioboto3
from app.core.config import settings


def build_object_key(prefix: str, safe_filename: str, ext: str) -> str:
    ts_id = uuid.uuid4().hex[:12]
    return str(PurePosixPath(prefix) / f"{ts_id}_{safe_filename}")


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
