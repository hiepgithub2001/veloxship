"""Schemas for the storage (file upload) endpoints."""

from pydantic import BaseModel


class UploadResultResponse(BaseModel):
    key: str
    mime_type: str
    size_bytes: int
    ext: str
    public_url: str | None = None
