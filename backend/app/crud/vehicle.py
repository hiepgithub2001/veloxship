"""Vehicle CRUD operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


async def list_vehicles(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    status: str | None = None,
    vehicle_type: str | None = None,
    latest_depot_id: int | None = None,
) -> tuple[list[Vehicle], int]:
    """List vehicles with pagination, search, and filters."""

    base_query = select(Vehicle)

    # Case-insensitive search on license_plate
    if search:
        search_term = search.strip()
        if search_term:
            base_query = base_query.where(
                func.lower(Vehicle.license_plate).like(
                    "%" + func.lower(search_term) + "%"
                )
            )

    # AND filters
    if status:
        base_query = base_query.where(Vehicle.status == status)
    if vehicle_type:
        base_query = base_query.where(Vehicle.vehicle_type == vehicle_type)
    if latest_depot_id is not None:
        base_query = base_query.where(Vehicle.latest_depot_id == latest_depot_id)

    # Total count
    count_query = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # Fetch paginated items ordered by created_at desc
    offset = (page - 1) * page_size
    items_query = base_query.order_by(Vehicle.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(items_query)
    items = list(result.scalars().unique().all())

    return items, total


async def get_vehicle(db: AsyncSession, vehicle_id: int) -> Vehicle | None:
    """Get a single vehicle by id."""
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    return result.scalars().unique().one_or_none()


async def get_vehicle_by_license_plate(db: AsyncSession, license_plate: str) -> Vehicle | None:
    """Get a single vehicle by license_plate."""
    result = await db.execute(
        select(Vehicle).where(Vehicle.license_plate == license_plate)
    )
    return result.scalars().unique().one_or_none()


async def create_vehicle(db: AsyncSession, *, payload: VehicleCreate) -> Vehicle:
    """Create a new vehicle record."""
    vehicle = Vehicle(
        license_plate=payload.license_plate,
        vehicle_type=payload.vehicle_type,
        max_weight_kg=payload.max_weight_kg,
        max_volume_m3=payload.max_volume_m3,
        latest_depot_id=payload.latest_depot_id,
        driver_id=payload.driver_id,
        status=payload.status or "active",
        images=payload.images,
    )
    db.add(vehicle)
    await db.flush()
    await db.refresh(vehicle)
    return vehicle


async def update_vehicle(db: AsyncSession, *, vehicle: Vehicle, payload: VehicleUpdate) -> Vehicle:
    """Partial update — only set fields that are explicitly provided."""
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)
    await db.flush()
    await db.refresh(vehicle)
    return vehicle

