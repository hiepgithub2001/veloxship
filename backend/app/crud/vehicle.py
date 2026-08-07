"""Vehicle CRUD operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.depot import Depot
from app.models.user import User
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
    items = list(result.scalars().all())

    # Batch-load driver and depot names
    await _load_driver_depot(db, items)

    return items, total


async def get_vehicle(db: AsyncSession, vehicle_id: int) -> Vehicle | None:
    """Get a single vehicle by id."""
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    if vehicle:
        await _load_driver_depot(db, [vehicle])
    return vehicle


async def get_vehicle_by_license_plate(db: AsyncSession, license_plate: str) -> Vehicle | None:
    """Get a single vehicle by license_plate."""
    result = await db.execute(
        select(Vehicle).where(Vehicle.license_plate == license_plate)
    )
    return result.scalar_one_or_none()


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
    )
    db.add(vehicle)
    await db.flush()
    await _load_driver_depot(db, [vehicle])
    return vehicle


async def update_vehicle(db: AsyncSession, *, vehicle: Vehicle, payload: VehicleUpdate) -> Vehicle:
    """Partial update — only set fields that are explicitly provided."""
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)
    await db.flush()
    await db.refresh(vehicle)
    await _load_driver_depot(db, [vehicle])
    return vehicle


# ─── Private helpers ─────────────────────────────────────────────────────────


async def _load_driver_depot(db: AsyncSession, vehicles: list[Vehicle]) -> None:
    """Batch-load driver_name (from users) and depot_name (from depots) onto vehicles."""
    driver_ids = [v.driver_id for v in vehicles if v.driver_id]
    depot_ids = [v.latest_depot_id for v in vehicles if v.latest_depot_id]

    # Load driver names
    driver_lookup: dict[int, str] = {}
    if driver_ids:
        result = await db.execute(
            select(User.id, User.full_name).where(User.id.in_(driver_ids))
        )
        for user_id, full_name in result.all():
            driver_lookup[user_id] = full_name

    # Load depot names
    depot_lookup: dict[int, str] = {}
    if depot_ids:
        result = await db.execute(
            select(Depot.id, Depot.name).where(Depot.id.in_(depot_ids))
        )
        for depot_id, name in result.all():
            depot_lookup[depot_id] = name

    # Assign to vehicle instances
    for v in vehicles:
        v.driver_name = driver_lookup.get(v.driver_id) if v.driver_id else None  # type: ignore[attr-defined]
        v.depot_name = depot_lookup.get(v.latest_depot_id) if v.latest_depot_id else None  # type: ignore[attr-defined]
