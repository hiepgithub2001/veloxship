"""Positions lookup API — derived from `users.metadata.position`."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import require_role
from app.crud import audit as audit_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.lookup import LookupItem, LookupList, LookupRename
from app.services import lookup_service

router = APIRouter(prefix="/positions", tags=["positions"])


@router.get("", response_model=LookupList)
async def list_positions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """List distinct positions with user counts."""
    rows = await lookup_service.list_lookup(db, "position")
    items = [LookupItem(name=name, user_count=count) for name, count in rows]
    return LookupList(items=items, total=len(items))


@router.patch("/{name}", response_model=LookupList)
async def rename_position(
    name: str,
    body: LookupRename,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Rename a position across all users."""
    await lookup_service.rename_lookup(db, "position", name, body.name)
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="iam.position.rename",
        details={"from": name, "to": body.name},
    )
    rows = await lookup_service.list_lookup(db, "position")
    items = [LookupItem(name=n, user_count=c) for n, c in rows]
    return LookupList(items=items, total=len(items))


@router.delete("/{name}", response_model=LookupList)
async def delete_position(
    name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Remove a position label from all users."""
    await lookup_service.delete_lookup(db, "position", name, in_use_code="POSITION_IN_USE")
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="iam.position.delete",
        details={"name": name},
    )
    rows = await lookup_service.list_lookup(db, "position")
    items = [LookupItem(name=n, user_count=c) for n, c in rows]
    return LookupList(items=items, total=len(items))
