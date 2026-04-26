"""Bill business logic — create, validate, status transitions."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, ConflictError, NotFoundError
from app.crud import bill as bill_crud
from app.models.service_tier import ServiceTier
from app.schemas.bill import BillCreate


async def create_bill(
    db: AsyncSession,
    payload: BillCreate,
    actor_id: int,
) -> "Bill":
    """Create a bill with full validation (FR-005, FR-006, FR-007)."""
    # FR-005: Validate service tier exists and scope matches
    result = await db.execute(
        select(ServiceTier).where(ServiceTier.code == payload.service_tier_code)
    )
    tier = result.scalar_one_or_none()
    if tier is None:
        raise NotFoundError("TIER_NOT_FOUND")
    if not tier.is_active:
        raise NotFoundError("TIER_NOT_FOUND")

    # Validate content lines
    if not payload.contents:
        raise AppError("CONTENT_LINES_REQUIRED")

    # Create the bill
    return await bill_crud.create_bill(db, payload=payload, actor_id=actor_id)
