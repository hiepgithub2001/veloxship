"""Vehicles API — list, create, update endpoints."""

import json
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.crud import vehicle as vehicle_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.vehicle import VehicleCreate, VehiclePage, VehicleRead, VehicleUpdate
from app.services import vehicle_service

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


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


@router.get("", response_model=VehiclePage)
async def list_vehicles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, min_length=1, max_length=100),
    status: str | None = Query(None),
    vehicle_type: str | None = Query(None),
    latest_depot_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List vehicles with pagination, search, and filters."""
    items, total = await vehicle_crud.list_vehicles(
        db,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        vehicle_type=vehicle_type,
        latest_depot_id=latest_depot_id,
    )
    return VehiclePage(
        items=[VehicleRead.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post("", response_model=VehicleRead, status_code=201)
async def create_vehicle(
    license_plate: str = Form(...),
    vehicle_type: str = Form(...),
    max_weight_kg: str = Form(...),
    max_volume_m3: str = Form(...),
    latest_depot_id: int | None = Form(None),
    driver_id: int | None = Form(None),
    status: str | None = Form(None),
    image_urls: str | None = Form(None, description="JSON array of S3 keys"),
    images: list[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new vehicle with optional image uploads."""
    payload = VehicleCreate(
        license_plate=license_plate,
        vehicle_type=vehicle_type,
        max_weight_kg=max_weight_kg,
        max_volume_m3=max_volume_m3,
        latest_depot_id=latest_depot_id,
        driver_id=driver_id,
        status=status,
        image_urls=_parse_image_urls(image_urls),
    )
    vehicle = await vehicle_service.create_vehicle(db, payload=payload, images=images)
    return VehicleRead.model_validate(vehicle)


@router.patch("/{vehicle_id}", response_model=VehicleRead)
async def update_vehicle(
    vehicle_id: int,
    license_plate: str | None = Form(None),
    vehicle_type: str | None = Form(None),
    max_weight_kg: str | None = Form(None),
    max_volume_m3: str | None = Form(None),
    latest_depot_id: int | None = Form(None),
    driver_id: int | None = Form(None),
    status: str | None = Form(None),
    image_urls: str | None = Form(None, description="JSON array of S3 keys"),
    images: list[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Partial update a vehicle with optional image uploads."""
    payload = VehicleUpdate(
        license_plate=license_plate,
        vehicle_type=vehicle_type,
        max_weight_kg=max_weight_kg,
        max_volume_m3=max_volume_m3,
        latest_depot_id=latest_depot_id,
        driver_id=driver_id,
        status=status,
        image_urls=_parse_image_urls(image_urls),
    )
    vehicle = await vehicle_service.update_vehicle(
        db, vehicle_id=vehicle_id, payload=payload, images=images
    )
    return VehicleRead.model_validate(vehicle)
