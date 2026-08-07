"""Storage API — file upload endpoint with magic-byte validation."""

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.storage import UploadResultResponse
from app.services.storage_service import upload_file

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/upload", response_model=UploadResultResponse, status_code=201)
async def upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    result = await upload_file(file)
    return result
