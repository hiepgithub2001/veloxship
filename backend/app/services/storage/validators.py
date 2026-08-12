"""File magic-byte validation using the filetype library."""

from __future__ import annotations

import filetype
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import FileTooLargeError, InvalidFileTypeError


ALLOWED_EXTENSIONS: set[str] = {
    "jpg",
    "jpeg",
    "png",
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
}

ALLOWED_MIME_TYPES: set[str] = {
    "image/jpeg",
    "image/png",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

WINDOWS_ILLEGAL_CHARS = {"<", ">", ":", '"', "/", "\\", "|", "?", "*"}


def _safe_filename(name: str) -> str:
    out = "".join(c if c not in WINDOWS_ILLEGAL_CHARS else "_" for c in name)
    return out.strip() or "unnamed"


def validate_file_size(size: int | None) -> None:
    """Validate that the file size does not exceed the maximum allowed bytes."""
    if size is not None and size > settings.UPLOAD_MAX_SIZE_BYTES:
        raise FileTooLargeError(
            details={"max_bytes": settings.UPLOAD_MAX_SIZE_BYTES, "received": size or 0}
        )


def detect_file_kind(header: bytes) -> filetype.Type:
    """Detect file format kind from magic bytes header."""
    kind = filetype.guess(header)
    if kind is None:
        raise InvalidFileTypeError(details={"reason": "unrecognized_format"})
    return kind


def validate_mime_type(detected_mime: str) -> None:
    """Validate detected MIME type against ALLOWED_MIME_TYPES."""
    if ALLOWED_MIME_TYPES and detected_mime not in ALLOWED_MIME_TYPES:
        raise InvalidFileTypeError(
            details={
                "detected_mime": detected_mime,
                "allowed": sorted(ALLOWED_MIME_TYPES),
            }
        )


def validate_file_extension(detected_ext: str, filename: str | None) -> None:
    """Validate detected or original extension against ALLOWED_EXTENSIONS."""
    original_ext = (filename or "").rsplit(".", 1)[-1].lower() if filename else ""
    if (
        ALLOWED_EXTENSIONS
        and detected_ext not in ALLOWED_EXTENSIONS
        and original_ext not in ALLOWED_EXTENSIONS
    ):
        raise InvalidFileTypeError(
            details={
                "detected_ext": detected_ext,
                "allowed": sorted(ALLOWED_EXTENSIONS),
            }
        )


async def validate_file(file: UploadFile) -> ValidationResult:
    """Orchestrate file validation steps for an UploadFile."""
    validate_file_size(file.size)

    header = await file.read(65536)
    await file.seek(0)

    kind = detect_file_kind(header)
    validate_mime_type(kind.mime)
    validate_file_extension(kind.extension, file.filename)

    size = file.size if file.size is not None else len(header)
    safe_name = _safe_filename(file.filename or f"upload.{kind.extension}")

    return ValidationResult(
        file=file,
        ext=kind.extension,
        mime_type=kind.mime,
        size=size,
        safe_filename=safe_name,
    )


class ValidationResult:
    __slots__ = ("file", "ext", "mime_type", "size", "safe_filename")

    def __init__(
        self,
        *,
        file: UploadFile,
        ext: str,
        mime_type: str,
        size: int,
        safe_filename: str,
    ):
        self.file = file
        self.ext = ext
        self.mime_type = mime_type
        self.size = size
        self.safe_filename = safe_filename
