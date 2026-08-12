"""API router for file upload operations."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.storage import UploadResultResponse
from app.services.storage_service import upload_file

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=UploadResultResponse, status_code=status.HTTP_201_CREATED)
async def upload_file_endpoint(
    upload_result: UploadResultResponse = Depends(upload_file),
    current_user: User = Depends(get_current_user),
) -> UploadResultResponse:
    """Upload a file (images, PDF, Word, Excel) to S3 storage.
    
    Validates file size, magic-byte format, MIME type, and extension before uploading.
    """
    return upload_result
