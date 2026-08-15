"""Depot CRUD operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.depot import Depot
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
    items = list(result.scalars().unique().all())

    return items, total


async def get_depot(db: AsyncSession, depot_id: int) -> Depot | None:
    """Get a single depot by id."""
    result = await db.execute(select(Depot).where(Depot.id == depot_id))
    return result.scalars().unique().one_or_none()


async def get_depot_by_code(db: AsyncSession, code: str) -> Depot | None:
    """Get a single depot by code."""
    result = await db.execute(select(Depot).where(Depot.code == code))
    return result.scalars().unique().one_or_none()


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
    await db.refresh(depot)
    return depot


async def update_depot(db: AsyncSession, *, depot: Depot, payload: DepotUpdate) -> Depot:
    """Partial update — only set fields that are explicitly provided."""
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(depot, field, value)
    await db.flush()
    await db.refresh(depot)
    return depot

