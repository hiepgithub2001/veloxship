"""Vehicle business logic — create, update with validation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, ConflictError, NotFoundError
from app.crud import vehicle as vehicle_crud
from app.models.depot import Depot
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


async def _validate_driver(db: AsyncSession, driver_id: int) -> None:
    """Raise AppError(DRIVER_NOT_FOUND) if user doesn't exist or is not active."""
    result = await db.execute(
        select(User.id).where(User.id == driver_id, User.is_active == True)  # noqa: E712
    )
    if result.scalar_one_or_none() is None:
        raise AppError("DRIVER_NOT_FOUND", status_code=422)


async def _validate_depot(db: AsyncSession, depot_id: int) -> None:
    """Raise AppError(DEPOT_NOT_FOUND) if depot doesn't exist."""
    result = await db.execute(select(Depot.id).where(Depot.id == depot_id))
    if result.scalar_one_or_none() is None:
        raise AppError("DEPOT_NOT_FOUND", status_code=422)


async def create_vehicle(db: AsyncSession, payload: VehicleCreate) -> Vehicle:
    """Create a vehicle after checking license_plate uniqueness and FK existence."""
    # 1. Check license_plate uniqueness
    existing = await vehicle_crud.get_vehicle_by_license_plate(db, payload.license_plate)
    if existing is not None:
        raise ConflictError("LICENSE_PLATE_EXISTS")

    # 2. Validate driver_id exists & is active if provided
    if payload.driver_id is not None:
        await _validate_driver(db, payload.driver_id)

    # 3. Validate latest_depot_id exists if provided
    if payload.latest_depot_id is not None:
        await _validate_depot(db, payload.latest_depot_id)

    # 4. Set default status='active' if not provided
    if payload.status is None:
        payload = payload.model_copy(update={"status": "active"})

    # 5. Delegate to CRUD
    return await vehicle_crud.create_vehicle(db, payload=payload)


async def update_vehicle(db: AsyncSession, vehicle_id: int, payload: VehicleUpdate) -> Vehicle:
    """Update a vehicle with uniqueness checks and FK validation."""
    # 1. Get vehicle or raise NotFoundError
    vehicle = await vehicle_crud.get_vehicle(db, vehicle_id)
    if vehicle is None:
        raise NotFoundError("VEHICLE_NOT_FOUND")

    update_data = payload.model_dump(exclude_unset=True)

    # 2. Check license_plate uniqueness (exclude self) if provided
    if "license_plate" in update_data and update_data["license_plate"] is not None:
        existing = await vehicle_crud.get_vehicle_by_license_plate(
            db, update_data["license_plate"]
        )
        if existing is not None and existing.id != vehicle_id:
            raise ConflictError("LICENSE_PLATE_EXISTS")

    # 3. Validate driver_id if provided
    if "driver_id" in update_data and update_data["driver_id"] is not None:
        await _validate_driver(db, update_data["driver_id"])

    # 4. Validate latest_depot_id if provided
    if "latest_depot_id" in update_data and update_data["latest_depot_id"] is not None:
        await _validate_depot(db, update_data["latest_depot_id"])

    # 5. Handle status idempotency — skip update if same value
    if "status" in update_data and update_data["status"] == vehicle.status:
        del update_data["status"]
        if not update_data:
            # Nothing to update, return vehicle as-is
            return vehicle
        # Rebuild payload without status
        payload = VehicleUpdate(**update_data)

    # 6. Delegate to CRUD
    return await vehicle_crud.update_vehicle(db, vehicle=vehicle, payload=payload)
