"""Location CRUD operations — provinces and wards."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.province import Province
from app.models.ward import Ward


async def list_provinces(db: AsyncSession) -> list[Province]:
    """Return all provinces ordered by name."""
    stmt = select(Province).order_by(Province.name)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_wards_by_province(db: AsyncSession, province_code: str) -> list[Ward]:
    """Return all wards belonging to a province, ordered by name."""
    stmt = (
        select(Ward)
        .where(Ward.province_code == province_code)
        .order_by(Ward.name)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
