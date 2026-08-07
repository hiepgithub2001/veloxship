"""Cloudflare R2 client factory (S3-compatible via aioboto3)."""
from __future__ import annotations

from contextlib import asynccontextmanager

import aioboto3
from app.core.config import settings


def _build_endpoint_url() -> str | None:
    if settings.R2_ENDPOINT_URL:
        return settings.R2_ENDPOINT_URL
    account_id = settings.R2_ACCOUNT_ID
    if not account_id:
        return None
    return f"https://{account_id}.r2.cloudflarestorage.com"


@asynccontextmanager
async def get_r2_client():
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=_build_endpoint_url(),
        region_name=settings.R2_REGION,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    ) as client:
        yield client
