"""Upload service layer — orchestrates validation → S3 upload → response."""
from __future__ import annotations

import structlog
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import UploadFailedError
from app.schemas.storage import UploadResultResponse
from app.services import storage as storage_helpers
from app.services.storage.validators import validate_and_upload

logger = structlog.get_logger()


async def upload_file(file: UploadFile) -> UploadResultResponse:
    result = await validate_and_upload(file)

    prefix = settings.UPLOAD_PREFIX.strip("/")
    key = storage_helpers.build_object_key(prefix, result.safe_filename, result.ext)
    public_url = storage_helpers.build_public_url(key)

    size = result.size

    try:
        file.file.seek(0)
        await storage_helpers.upload_to_s3(
            file_obj=file.file,
            key=key,
            content_type=result.mime_type,
            size_bytes=size,
        )
    except UploadFailedError:
        raise
    except Exception as exc:
        logger.error("upload.failed", key=key, error=str(exc))
        raise UploadFailedError(details={"key": key, "error": str(exc)}) from exc

    logger.info("upload.success", key=key, mime=result.mime_type, ext=result.ext, size=size)

    return UploadResultResponse(
        key=key,
        mime_type=result.mime_type,
        size_bytes=size,
        ext=result.ext,
        public_url=public_url,
    )
