"""Tracking number generator using PostgreSQL sequence."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings


async def next_tracking_number(db: AsyncSession) -> str:
    """Generate the next unique tracking number from the DB sequence.

    Format: {PREFIX}{seq:07d}  e.g. NL0000001
    """
    result = await db.execute(text("SELECT nextval('bill_tracking_seq')"))
    seq_value = result.scalar_one()
    return f"{settings.TRACKING_NUMBER_PREFIX}{seq_value:07d}"
