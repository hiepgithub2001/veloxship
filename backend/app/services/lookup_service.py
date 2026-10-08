"""Lookup (department/position) business logic over `users.metadata`."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.crud import user as user_crud


async def list_lookup(db: AsyncSession, key: str) -> list[tuple[str, int]]:
    """Return distinct metadata values with usage counts."""
    return await user_crud.list_distinct_metadata(db, key)


async def rename_lookup(db: AsyncSession, key: str, old: str, new: str) -> int:
    """Rename a metadata value across users; returns rows updated."""
    if old == new:
        return 0
    return await user_crud.rename_metadata_value(db, key, old, new)


async def delete_lookup(
    db: AsyncSession, key: str, name: str, *, in_use_code: str
) -> int:
    """Delete a metadata value; blocks when still referenced by users."""
    values = await user_crud.list_distinct_metadata(db, key)
    count = next((c for n, c in values if n == name), 0)
    if count > 0:
        raise ConflictError(in_use_code)
    return await user_crud.delete_metadata_value(db, key, name)
