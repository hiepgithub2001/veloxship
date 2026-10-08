"""Departments lookup API — derived from `users.metadata.department`."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import require_role
from app.crud import audit as audit_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.lookup import LookupItem, LookupList, LookupRename
from app.services import lookup_service

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=LookupList)
async def list_departments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """List distinct departments with user counts."""
    rows = await lookup_service.list_lookup(db, "department")
    items = [LookupItem(name=name, user_count=count) for name, count in rows]
    return LookupList(items=items, total=len(items))


@router.patch("/{name}", response_model=LookupList)
async def rename_department(
    name: str,
    body: LookupRename,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Rename a department across all users."""
    await lookup_service.rename_lookup(db, "department", name, body.name)
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="iam.department.rename",
        details={"from": name, "to": body.name},
    )
    rows = await lookup_service.list_lookup(db, "department")
    items = [LookupItem(name=n, user_count=c) for n, c in rows]
    return LookupList(items=items, total=len(items))


@router.delete("/{name}", response_model=LookupList)
async def delete_department(
    name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Remove a department label from all users."""
    await lookup_service.delete_lookup(db, "department", name, in_use_code="DEPARTMENT_IN_USE")
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="iam.department.delete",
        details={"name": name},
    )
    rows = await lookup_service.list_lookup(db, "department")
    items = [LookupItem(name=n, user_count=c) for n, c in rows]
    return LookupList(items=items, total=len(items))
