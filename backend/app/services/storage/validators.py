"""File magic-byte validation using the filetype library."""
from __future__ import annotations

import filetype
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import FileTooLargeError, InvalidFileTypeError


ALLOWED_EXTENSIONS: set[str] = set()
ALLOWED_MIME_TYPES: set[str] = set()

if settings.ALLOWED_EXTENSIONS:
    ALLOWED_EXTENSIONS = {e.strip().lower() for e in settings.ALLOWED_EXTENSIONS.split(",") if e.strip()}

if settings.ALLOWED_MIME_TYPES:
    ALLOWED_MIME_TYPES = {m.strip() for m in settings.ALLOWED_MIME_TYPES.split(",") if m.strip()}

WINDOWS_ILLEGAL_CHARS = {"<", ">", ":", '"', "/", "\\", "|", "?", "*"}


def _safe_filename(name: str) -> str:
    out = "".join(c if c not in WINDOWS_ILLEGAL_CHARS else "_" for c in name)
    return out.strip() or "unnamed"


async def validate_and_upload(file: UploadFile) -> ValidationResult:
    if file.size is not None and file.size > settings.UPLOAD_MAX_SIZE_BYTES:
        raise FileTooLargeError(
            details={"max_bytes": settings.UPLOAD_MAX_SIZE_BYTES, "received": file.size or 0}
        )

    header = await file.read(65536)
    await file.seek(0)

    kind = filetype.guess(header)
    if kind is None:
        raise InvalidFileTypeError(details={"reason": "unrecognized_format"})

    detected_mime = kind.mime
    detected_ext = kind.extension

    if ALLOWED_MIME_TYPES and detected_mime not in ALLOWED_MIME_TYPES:
        raise InvalidFileTypeError(
            details={"detected_mime": detected_mime, "allowed": sorted(ALLOWED_MIME_TYPES)}
        )

    original_ext = (file.filename or "").rsplit(".", 1)[-1].lower() if file.filename else ""
    if ALLOWED_EXTENSIONS and detected_ext not in ALLOWED_EXTENSIONS and original_ext not in ALLOWED_EXTENSIONS:
        raise InvalidFileTypeError(
            details={"detected_ext": detected_ext, "allowed": sorted(ALLOWED_EXTENSIONS)}
        )

    size = file.size if file.size is not None else len(header)
    ext = detected_ext
    safe_name = _safe_filename(file.filename or f"upload.{detected_ext}")

    return ValidationResult(
        ext=ext,
        mime_type=detected_mime,
        size=size,
        safe_filename=safe_name,
    )


class ValidationResult:
    __slots__ = ("ext", "mime_type", "size", "safe_filename")

    def __init__(self, *, ext: str, mime_type: str, size: int, safe_filename: str):
        self.ext = ext
        self.mime_type = mime_type
        self.size = size
        self.safe_filename = safe_filename
