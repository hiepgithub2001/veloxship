"""Unit tests for storage validators."""
from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi import UploadFile

from app.core.config import Settings
from app.core.exceptions import FileTooLargeError, InvalidFileTypeError
from app.services.storage import validators


JPEG_HEADER = b"\xff\xd8\xff\xe0\x00\x10JFIF"
PNG_HEADER = b"\x89PNG\r\n\x1a\n\x00\x00"
PDF_HEADER = b"%PDF-1.4\n\x00\x00"


def _upload_file(
    filename: str = "test.jpg",
    content_type: str = "image/jpeg",
    size: int | None = 100,
    header: bytes = JPEG_HEADER,
) -> UploadFile:
    file = MagicMock(spec=UploadFile)
    file.filename = filename
    file.content_type = content_type
    file.size = size
    file.read = pytest.mock.AsyncMock(return_value=header)
    file.seek = pytest.mock.AsyncMock()
    file.file = io.BytesIO(header)
    return file


@pytest.mark.asyncio
async def test_rejects_oversized_file():
    with patch.object(validators.settings, "UPLOAD_MAX_SIZE_BYTES", 100):
        with pytest.raises(FileTooLargeError):
            await validators.validate_and_upload(_upload_file(size=200))


@pytest.mark.asyncio
async def test_rejects_unrecognized_format():
    with pytest.raises(InvalidFileTypeError):
        await validators.validate_and_upload(_upload_file(header=b"\x00\x01\x02\x03"))


@pytest.mark.asyncio
async def test_accepts_jpeg_returns_result():
    with patch.object(validators.settings, "ALLOWED_EXTENSIONS", "jpg,jpeg,png"):
        with patch.object(validators.settings, "ALLOWED_MIME_TYPES", "jpg:image/jpeg,png:image/png"):
            result = await validators.validate_and_upload(_upload_file())
    assert result.ext == "jpeg"
    assert result.mime_type == "image/jpeg"
    assert result.safe_filename == "test.jpg"


@pytest.mark.asyncio
async def test_rejects_disallowed_mime():
    with patch.object(validators.settings, "ALLOWED_MIME_TYPES", "image/png"):
        with pytest.raises(InvalidFileTypeError):
            await validators.validate_and_upload(_upload_file(header=JPEG_HEADER))
