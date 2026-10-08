"""User CRUD operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password, verify_password
from app.models.user import User


async def get_by_username(db: AsyncSession, username: str) -> User | None:
    """Fetch a user by username (case-insensitive)."""
    result = await db.execute(
        select(User).where(User.username == username.lower())
    )
    return result.scalar_one_or_none()


async def get_by_phone(db: AsyncSession, phone: str) -> User | None:
    """Fetch a user by phone number."""
    result = await db.execute(select(User).where(User.phone == phone))
    return result.scalar_one_or_none()


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    """Fetch a user by id with its role eager-loaded."""
    result = await db.execute(
        select(User).options(selectinload(User.role_ref)).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def authenticate(db: AsyncSession, username: str, password: str) -> User | None:
    """Verify credentials and return the user, or None if invalid."""
    user = await get_by_username(db, username)
    if user is None or not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


def _build_metadata(department: str | None, position: str | None, employee_code: str | None) -> dict | None:
    """Compose the `metadata` JSONB payload for a user record."""
    metadata: dict = {}
    if department:
        metadata["department"] = department.strip()
    if position:
        metadata["position"] = position.strip()
    if employee_code:
        metadata["employee_code"] = employee_code.strip()
    return metadata or None


async def create_user(
    db: AsyncSession,
    *,
    username: str,
    full_name: str,
    password_hash: str,
    role: str = "operator",
    phone: str | None = None,
    department: str | None = None,
    position: str | None = None,
    employee_code: str | None = None,
    depot_id: int | None = None,
) -> User:
    """Create a new user with hashed password."""
    user = User(
        username=username.lower(),
        full_name=full_name,
        password_hash=password_hash,
        role=role,
        phone=phone,
        user_metadata=_build_metadata(department, position, employee_code),
        depot_id=depot_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, *, user: User, data: dict) -> User:
    """Partial update — only set fields that are explicitly provided."""
    metadata_fields = ("department", "position", "employee_code")
    for field in list(data):
        if field in metadata_fields:
            continue
        setattr(user, field, data[field])

    # Merge metadata changes onto the existing JSONB payload.
    if any(field in data for field in metadata_fields):
        merged = dict(user.user_metadata or {})
        for field in metadata_fields:
            if field not in data:
                continue
            value = data[field]
            if value:
                merged[field] = value.strip()
            else:
                merged.pop(field, None)
        user.user_metadata = merged or None

    await db.flush()
    await db.refresh(user)
    return user


async def set_password(db: AsyncSession, *, user: User, password: str) -> User:
    """Set a new (hashed) password for a user."""
    user.password_hash = hash_password(password)
    await db.flush()
    await db.refresh(user)
    return user


async def list_users(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    role: str | None = None,
    depot_id: int | None = None,
    department: str | None = None,
    position: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[User], int]:
    """List users with pagination, unaccent search, and filters."""
    base_query = select(User).options(selectinload(User.role_ref))

    if is_active is not None:
        base_query = base_query.where(User.is_active == is_active)
    if role:
        base_query = base_query.where(User.role == role)
    if depot_id is not None:
        base_query = base_query.where(User.depot_id == depot_id)
    if department:
        base_query = base_query.where(
            User.user_metadata["department"].astext == department
        )
    if position:
        base_query = base_query.where(User.user_metadata["position"].astext == position)

    if search and search.strip():
        term = func.unaccent(func.lower(search.strip()))
        base_query = base_query.where(
            func.unaccent(func.lower(User.full_name)).like(f"%{term}%")
            | func.unaccent(func.lower(User.username)).like(f"%{term}%")
            | func.unaccent(func.lower(func.coalesce(User.phone, ""))).like(f"%{term}%")
        )

    count_query = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    items_query = base_query.order_by(User.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(items_query)
    items = list(result.scalars().unique().all())
    return items, total


async def list_distinct_metadata(db: AsyncSession, key: str) -> list[tuple[str, int]]:
    """Return distinct non-null `metadata[key]` values with usage counts."""
    expr = User.user_metadata[key].astext
    stmt = (
        select(expr.label("name"), func.count(User.id).label("user_count"))
        .where(expr.isnot(None))
        .group_by(expr)
        .order_by(expr)
    )
    result = await db.execute(stmt)
    return [(row.name, row.user_count) for row in result.all()]


async def rename_metadata_value(db: AsyncSession, key: str, old: str, new: str) -> int:
    """Rename a metadata value across users; returns the number of rows updated."""
    expr = User.user_metadata[key].astext
    result = await db.execute(select(User).where(expr == old))
    users = result.scalars().all()
    for user in users:
        merged = dict(user.user_metadata or {})
        merged[key] = new
        user.user_metadata = merged
    await db.flush()
    return len(users)


async def delete_metadata_value(db: AsyncSession, key: str, name: str) -> int:
    """Remove a metadata value across users; returns the number of rows updated."""
    expr = User.user_metadata[key].astext
    result = await db.execute(select(User).where(expr == name))
    users = result.scalars().all()
    for user in users:
        merged = dict(user.user_metadata or {})
        merged.pop(key, None)
        user.user_metadata = merged or None
    await db.flush()
    return len(users)
