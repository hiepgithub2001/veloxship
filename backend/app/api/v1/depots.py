"""Depots API — list, create, update endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.crud import depot as depot_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.depot import DepotCreate, DepotPage, DepotRead, DepotUpdate
from app.services import depot_service

router = APIRouter(prefix="/depots", tags=["depots"])


@router.get("", response_model=DepotPage)
async def list_depots(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, min_length=1, max_length=100),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List depots with pagination, search, and active filter."""
    items, total = await depot_crud.list_depots(
        db, page=page, page_size=page_size, search=search, is_active=is_active
    )
    return DepotPage(
        items=[DepotRead.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post("", response_model=DepotRead, status_code=201)
async def create_depot(
    body: DepotCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new depot."""
    depot = await depot_service.create_depot(db, body)
    return DepotRead.model_validate(depot)


@router.patch("/{depot_id}", response_model=DepotRead)
async def update_depot(
    depot_id: int,
    body: DepotUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Partial update a depot."""
    depot = await depot_service.update_depot(db, depot_id, body)
    return DepotRead.model_validate(depot)
