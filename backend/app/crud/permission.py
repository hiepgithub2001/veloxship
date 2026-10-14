"""Permission CRUD — dynamic roles and role→action grants."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.permission import Role, RolePermission
from app.models.user import User


async def get_role_permission_actions(db: AsyncSession, role: str) -> set[str]:
    """Return the set of every action granted directly to `role`."""
    stmt = select(RolePermission.action).where(RolePermission.role == role)
    result = await db.execute(stmt)
    return set(result.scalars().all())


async def list_roles(db: AsyncSession) -> list[Role]:
    """List all roles (with permissions eager-loaded), ordered by code."""
    stmt = (
        select(Role)
        .options(selectinload(Role.permissions))
        .order_by(Role.code.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())


async def get_role(db: AsyncSession, code: str) -> Role | None:
    """Fetch a single role with its permissions eager-loaded."""
    stmt = (
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.code == code)
    )
    result = await db.execute(stmt)
    return result.scalars().unique().one_or_none()


async def get_role_by_name(db: AsyncSession, name: str) -> Role | None:
    """Fetch a role by exact (case-insensitive) display name."""
    stmt = select(Role).where(func.lower(Role.name) == name.lower())
    result = await db.execute(stmt)
    return result.scalars().unique().one_or_none()


async def create_role(
    db: AsyncSession, *, code: str, name: str, description: str | None
) -> Role:
    """Create a new role."""
    role = Role(code=code, name=name, description=description)
    db.add(role)
    await db.flush()
    return await get_role(db, role.code)


async def update_role(
    db: AsyncSession, *, role: Role, name: str, description: str | None, is_active: bool
) -> Role:
    """Update a role's display name / description / active flag (code is immutable)."""
    role.name = name
    role.description = description
    role.is_active = is_active
    await db.flush()
    return await get_role(db, role.code)


async def delete_role(db: AsyncSession, *, role: Role) -> None:
    """Delete a role (its role_permissions cascade at the DB level)."""
    await db.delete(role)
    await db.flush()


async def set_role_actions(db: AsyncSession, *, role: Role, actions: list[str]) -> Role:
    """Replace the full set of actions granted to a role."""
    role.permissions.clear()
    for action in actions:
        role.permissions.append(RolePermission(role=role.code, action=action))
    await db.flush()
    return await get_role(db, role.code)


async def count_users_by_role(db: AsyncSession, role: str) -> int:
    """Return the number of users currently assigned to `role`."""
    stmt = select(func.count()).select_from(User).where(User.role == role)
    result = await db.execute(stmt)
    return result.scalar_one()
