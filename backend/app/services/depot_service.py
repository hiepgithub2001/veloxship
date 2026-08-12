"""Depot business logic — create, update with validation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, ConflictError, NotFoundError
from app.crud import depot as depot_crud
from app.models.depot import Depot
from app.models.ward import Ward
from app.schemas.depot import DepotCreate, DepotUpdate


async def _validate_ward_code(db: AsyncSession, ward_code: str) -> None:
    """Raise AppError(WARD_NOT_FOUND) if ward_code does not exist."""
    result = await db.execute(select(Ward.code).where(Ward.code == ward_code))
    if result.scalar_one_or_none() is None:
        raise AppError("WARD_NOT_FOUND", status_code=422)


async def create_depot(db: AsyncSession, payload: DepotCreate) -> Depot:
    """Create a depot after checking code uniqueness and ward existence."""
    # 1. Check code uniqueness
    existing = await depot_crud.get_depot_by_code(db, payload.code)
    if existing is not None:
        raise ConflictError("DEPOT_CODE_EXISTS")

    # 2. Validate ward_code exists if provided
    if payload.ward_code:
        await _validate_ward_code(db, payload.ward_code)

    # 3. Delegate to CRUD
    return await depot_crud.create_depot(db, payload=payload)


async def update_depot(db: AsyncSession, depot_id: int, payload: DepotUpdate) -> Depot:
    """Update a depot with ward validation and is_active idempotency."""
    # 1. Get depot or raise NotFoundError
    depot = await depot_crud.get_depot(db, depot_id)
    if depot is None:
        raise NotFoundError("DEPOT_NOT_FOUND")

    # 2. Validate ward_code if provided
    update_data = payload.model_dump(exclude_unset=True)
    if "ward_code" in update_data and update_data["ward_code"] is not None:
        await _validate_ward_code(db, update_data["ward_code"])

    # 3. Handle is_active idempotency — skip update if same value
    if "is_active" in update_data and update_data["is_active"] == depot.is_active:
        # Remove is_active from the update to preserve updated_at
        del update_data["is_active"]
        if not update_data:
            # Nothing to update, return depot as-is
            return depot
        # Rebuild payload without is_active
        payload = DepotUpdate(**update_data)

    # 4. Delegate to CRUD
    return await depot_crud.update_depot(db, depot=depot, payload=payload)
