"""Depot CRUD operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.depot import Depot
from app.models.province import Province
from app.models.ward import Ward
from app.schemas.depot import DepotCreate, DepotUpdate


async def list_depots(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[Depot], int]:
    """List depots with pagination, unaccent search, and is_active filter."""

    base_query = select(Depot)

    # Apply is_active filter
    if is_active is not None:
        base_query = base_query.where(Depot.is_active == is_active)

    # Apply unaccent search on name and code
    if search:
        search_term = search.strip()
        if search_term:
            base_query = base_query.where(
                func.unaccent(func.lower(Depot.name)).like(
                    "%" + func.unaccent(func.lower(search_term)) + "%"
                )
                | func.unaccent(func.lower(Depot.code)).like(
                    "%" + func.unaccent(func.lower(search_term)) + "%"
                )
            )

    # Total count
    count_query = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # Fetch paginated items ordered by created_at desc
    offset = (page - 1) * page_size
    items_query = base_query.order_by(Depot.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(items_query)
    items = list(result.scalars().all())

    # Eager-load ward and province names for the fetched items
    await _load_ward_province(db, items)

    return items, total


async def get_depot(db: AsyncSession, depot_id: int) -> Depot | None:
    """Get a single depot by id."""
    result = await db.execute(select(Depot).where(Depot.id == depot_id))
    depot = result.scalar_one_or_none()
    if depot:
        await _load_ward_province(db, [depot])
    return depot


async def get_depot_by_code(db: AsyncSession, code: str) -> Depot | None:
    """Get a single depot by code."""
    result = await db.execute(select(Depot).where(Depot.code == code))
    return result.scalar_one_or_none()


async def create_depot(db: AsyncSession, *, payload: DepotCreate) -> Depot:
    """Create a new depot record."""
    depot = Depot(
        code=payload.code,
        name=payload.name,
        phone=payload.phone,
        address_detail=payload.address_detail,
        ward_code=payload.ward_code,
        images=payload.images,
    )
    db.add(depot)
    await db.flush()
    await _load_ward_province(db, [depot])
    return depot


async def update_depot(db: AsyncSession, *, depot: Depot, payload: DepotUpdate) -> Depot:
    """Partial update — only set fields that are explicitly provided."""
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(depot, field, value)
    await db.flush()
    await db.refresh(depot)
    await _load_ward_province(db, [depot])
    return depot


# ─── Private helpers ─────────────────────────────────────────────────────────


async def _load_ward_province(db: AsyncSession, depots: list[Depot]) -> None:
    """Attach ward_name, province_code, province_name as transient attributes."""
    ward_codes = [d.ward_code for d in depots if d.ward_code]
    if not ward_codes:
        for d in depots:
            d.ward_name = None  # type: ignore[attr-defined]
            d.province_code = None  # type: ignore[attr-defined]
            d.province_name = None  # type: ignore[attr-defined]
        return

    # Fetch wards with province in a single query
    result = await db.execute(
        select(Ward.code, Ward.name, Province.code, Province.name)
        .join(Province, Ward.province_code == Province.code)
        .where(Ward.code.in_(ward_codes))
    )
    lookup: dict[str, tuple[str, str, str]] = {}
    for ward_code, ward_name, province_code, province_name in result.all():
        lookup[ward_code] = (ward_name, province_code, province_name)

    for d in depots:
        if d.ward_code and d.ward_code in lookup:
            ward_name, province_code, province_name = lookup[d.ward_code]
            d.ward_name = ward_name  # type: ignore[attr-defined]
            d.province_code = province_code  # type: ignore[attr-defined]
            d.province_name = province_name  # type: ignore[attr-defined]
        else:
            d.ward_name = None  # type: ignore[attr-defined]
            d.province_code = None  # type: ignore[attr-defined]
            d.province_name = None  # type: ignore[attr-defined]
