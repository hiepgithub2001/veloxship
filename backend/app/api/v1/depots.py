"""Depots API — list, create, update endpoints."""

import json
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.crud import depot as depot_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.depot import DepotCreate, DepotPage, DepotRead, DepotUpdate
from app.services import depot_service

router = APIRouter(prefix="/depots", tags=["depots"])


def _parse_image_urls(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, list):
            raise ValueError("not a list")
        for item in parsed:
            if not isinstance(item, str):
                raise ValueError("item not str")
        return parsed
    except (ValueError, json.JSONDecodeError) as exc:
        raise RequestValidationError(
            [{"loc": ("body", "image_urls"), "msg": "Danh sách ảnh không hợp lệ."}]
        ) from exc


@router.get("", response_model=DepotPage)
async def list_depots(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, min_length=1, max_length=100),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List depots with pagination, search, and active filter."""
    items, total = await depot_crud.list_depots(
        db, page=page, page_size=page_size, search=search, is_active=is_active
    )
    return DepotPage(
        items=[DepotRead.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post("", response_model=DepotRead, status_code=201)
async def create_depot(
    code: str = Form(...),
    name: str = Form(...),
    phone: str = Form(...),
    address_detail: str = Form(...),
    ward_code: str | None = Form(None),
    image_urls: str | None = Form(None, description="JSON array of S3 keys"),
    images: list[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new depot with optional image uploads."""
    payload = DepotCreate(
        code=code,
        name=name,
        phone=phone,
        address_detail=address_detail,
        ward_code=ward_code,
        image_urls=_parse_image_urls(image_urls),
    )
    depot = await depot_service.create_depot(db, payload=payload, images=images)
    return DepotRead.model_validate(depot)


@router.patch("/{depot_id}", response_model=DepotRead)
async def update_depot(
    depot_id: int,
    name: str | None = Form(None),
    phone: str | None = Form(None),
    address_detail: str | None = Form(None),
    ward_code: str | None = Form(None),
    is_active: bool | None = Form(None),
    image_urls: str | None = Form(None, description="JSON array of S3 keys"),
    images: list[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Partial update a depot with optional image uploads."""
    payload = DepotUpdate(
        name=name,
        phone=phone,
        address_detail=address_detail,
        ward_code=ward_code,
        is_active=is_active,
        image_urls=_parse_image_urls(image_urls),
    )
    depot = await depot_service.update_depot(
        db, depot_id=depot_id, payload=payload, images=images
    )
    return DepotRead.model_validate(depot)
