"""AWS S3 client factory (via aioboto3)."""
from __future__ import annotations

from contextlib import asynccontextmanager

import aioboto3
from app.core.config import settings


@asynccontextmanager
async def get_s3_client():
    session = aioboto3.Session()
    kwargs = {
        "service_name": "s3",
        "region_name": settings.S3_REGION,
        "aws_access_key_id": settings.S3_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.S3_SECRET_ACCESS_KEY,
    }
    if settings.S3_ENDPOINT_URL:
        kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL

    async with session.client(**kwargs) as client:
        yield client
