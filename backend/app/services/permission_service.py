"""Role & role-permission business logic — create, update, delete, grant actions."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, ConflictError, NotFoundError
from app.core.permissions import ADMIN_ROLE
from app.crud import permission as permission_crud
from app.models.permission import Role
from app.schemas.permission import RoleCreate, RolePermissionsUpdate, RoleUpdate


async def create_role(db: AsyncSession, payload: RoleCreate) -> Role:
    """Create a role after checking code/name uniqueness."""
    if await permission_crud.get_role(db, payload.code) is not None:
        raise ConflictError("ROLE_CODE_EXISTS")
    if await permission_crud.get_role_by_name(db, payload.name) is not None:
        raise ConflictError("ROLE_NAME_EXISTS")
    return await permission_crud.create_role(
        db,
        code=payload.code,
        name=payload.name,
        description=payload.description,
    )


async def update_role(db: AsyncSession, code: str, payload: RoleUpdate) -> Role:
    """Update a role's name/description/active flag (code is immutable)."""
    role = await permission_crud.get_role(db, code)
    if role is None:
        raise NotFoundError("ROLE_NOT_FOUND")

    data = payload.model_dump(exclude_unset=True)
    new_name = data.get("name", role.name)
    if new_name != role.name:
        existing = await permission_crud.get_role_by_name(db, new_name)
        if existing is not None and existing.code != role.code:
            raise ConflictError("ROLE_NAME_EXISTS")

    return await permission_crud.update_role(
        db,
        role=role,
        name=new_name,
        description=data.get("description", role.description),
        is_active=data.get("is_active", role.is_active),
    )


async def delete_role(db: AsyncSession, code: str) -> None:
    """Delete a role, guarding the reserved admin role and roles still in use."""
    role = await permission_crud.get_role(db, code)
    if role is None:
        raise NotFoundError("ROLE_NOT_FOUND")
    if code == ADMIN_ROLE:
        raise AppError("CANNOT_DELETE_ADMIN_ROLE", status_code=409)
    if await permission_crud.count_users_by_role(db, code) > 0:
        raise ConflictError("ROLE_IN_USE")
    await permission_crud.delete_role(db, role=role)


async def set_role_actions(db: AsyncSession, code: str, payload: RolePermissionsUpdate) -> Role:
    """Replace the full action set granted to a role."""
    role = await permission_crud.get_role(db, code)
    if role is None:
        raise NotFoundError("ROLE_NOT_FOUND")
    return await permission_crud.set_role_actions(db, role=role, actions=payload.actions)
