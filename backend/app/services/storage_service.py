"""Upload service layer — orchestrates validation → S3 upload → response."""

from __future__ import annotations

import structlog
from fastapi import File, UploadFile

from app.core.config import settings
from app.core.exceptions import UploadFailedError
from app.schemas.storage import UploadResultResponse
from app.services import storage as storage_helpers
from app.services.storage.validators import validate_file

logger = structlog.get_logger()


async def upload_file(file: UploadFile = File(...)) -> UploadResultResponse:
    """Validate and upload a file to S3. Can be used directly or as a FastAPI dependency."""
    validated = await validate_file(file)

    prefix = settings.UPLOAD_PREFIX.strip("/")
    key = storage_helpers.build_object_key(
        prefix, validated.safe_filename, validated.ext
    )

    size = validated.size

    try:
        validated.file.file.seek(0)
        async with storage_helpers.get_s3_client() as s3:
            await s3.upload_fileobj(
                Fileobj=validated.file.file, Bucket=settings.S3_BUCKET_NAME, Key=key
            )
    except UploadFailedError:
        raise
    except Exception as exc:
        logger.error("upload.failed", key=key, error=str(exc))
        raise UploadFailedError(details={"key": key, "error": str(exc)}) from exc

    logger.info(
        "upload.success",
        key=key,
        mime=validated.mime_type,
        ext=validated.ext,
        size=size,
    )

    return UploadResultResponse(
        key=key,
        mime_type=validated.mime_type,
        size_bytes=size,
        ext=validated.ext,
    )
