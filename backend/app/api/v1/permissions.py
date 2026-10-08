"""Roles & permissions API — dynamic role CRUD, role grants, and the action catalogue."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import require_role
from app.core.permissions import PERMISSION_CATALOG
from app.crud import audit as audit_crud
from app.crud import permission as permission_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.permission import (
    PermissionCatalogRead,
    RoleCreate,
    RolePermissionsUpdate,
    RoleRead,
    RoleUpdate,
)
from app.services import permission_service

router = APIRouter(tags=["roles"])


@router.get("/permissions/catalog", response_model=PermissionCatalogRead)
async def get_catalog(current_user: User = Depends(require_role("admin"))):
    """Return every assignable action grouped by module."""
    return PermissionCatalogRead(modules=PERMISSION_CATALOG)


@router.get("/roles", response_model=list[RoleRead])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """List all roles with their granted actions and assigned-user count."""
    roles = await permission_crud.list_roles(db)
    result = []
    for role in roles:
        user_count = await permission_crud.count_users_by_role(db, role.code)
        result.append(
            RoleRead(
                code=role.code,
                name=role.name,
                description=role.description,
                is_active=role.is_active,
                actions=[p.action for p in role.permissions],
                user_count=user_count,
            )
        )
    return result


@router.post("/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    body: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Create a new role."""
    role = await permission_service.create_role(db, body)
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="iam.role.create",
        entity_type="role",
        details={"code": role.code, "name": role.name},
    )
    return RoleRead(
        code=role.code,
        name=role.name,
        description=role.description,
        is_active=role.is_active,
        actions=[],
    )


@router.patch("/roles/{code}", response_model=RoleRead)
async def update_role(
    code: str,
    body: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Update a role's name/description/active flag."""
    role = await permission_service.update_role(db, code, body)
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="iam.role.update",
        entity_type="role",
        details={"code": role.code, "name": role.name},
    )
    return RoleRead(
        code=role.code,
        name=role.name,
        description=role.description,
        is_active=role.is_active,
        actions=[p.action for p in role.permissions],
    )


@router.delete("/roles/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Delete a role (guarded against the reserved admin role and roles in use)."""
    await permission_service.delete_role(db, code)
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="iam.role.delete",
        entity_type="role",
        details={"code": code},
    )


@router.put("/roles/{code}/permissions", response_model=RoleRead)
async def set_role_permissions(
    code: str,
    body: RolePermissionsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Replace the full action set granted to a role."""
    role = await permission_service.set_role_actions(db, code, body)
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="iam.role.permissions",
        entity_type="role",
        details={"code": role.code, "action_count": len(body.actions)},
    )
    return RoleRead(
        code=role.code,
        name=role.name,
        description=role.description,
        is_active=role.is_active,
        actions=[p.action for p in role.permissions],
    )
