"""Customers API — read-only customer directory.

Customers are introduced by bill creation for now; a manual customer form is
intentionally out of scope.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.crud import customer as customer_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.customer import CustomerPage, CustomerRead

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=CustomerPage)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, min_length=1, max_length=100),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List customer profiles created while bills are recorded."""
    items, total = await customer_crud.list_customers(
        db,
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active,
    )
    return CustomerPage(
        items=[CustomerRead.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return one customer profile for directory inspection."""
    customer = await customer_crud.get_customer(db, customer_id)
    if customer is None:
        raise NotFoundError("CUSTOMER_NOT_FOUND")
    return CustomerRead.model_validate(customer)
