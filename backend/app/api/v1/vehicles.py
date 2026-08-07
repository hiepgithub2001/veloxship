"""Vehicles API — list, create, update endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.crud import vehicle as vehicle_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.vehicle import VehicleCreate, VehiclePage, VehicleRead, VehicleUpdate
from app.services import vehicle_service

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


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
    body: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new vehicle."""
    vehicle = await vehicle_service.create_vehicle(db, body)
    return VehicleRead.model_validate(vehicle)


@router.patch("/{vehicle_id}", response_model=VehicleRead)
async def update_vehicle(
    vehicle_id: int,
    body: VehicleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Partial update a vehicle."""
    vehicle = await vehicle_service.update_vehicle(db, vehicle_id, body)
    return VehicleRead.model_validate(vehicle)
