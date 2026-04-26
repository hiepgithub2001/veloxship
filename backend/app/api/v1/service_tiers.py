"""Service tiers API."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.service_tier import ServiceTier
from app.schemas.service_tier import ServiceTierRead

router = APIRouter(prefix="/service-tiers", tags=["service-tiers"])


@router.get("", response_model=list[ServiceTierRead])
async def list_service_tiers(
    scope: str | None = Query(None, description="Filter by scope: domestic | international"),
    db: AsyncSession = Depends(get_db),
):
    """Return the active service-tier catalogue, optionally filtered by scope."""
    stmt = select(ServiceTier).where(ServiceTier.is_active.is_(True))
    if scope:
        stmt = stmt.where(ServiceTier.scope == scope)
    result = await db.execute(stmt)
    return result.scalars().all()
