"""Customers API — directory, edit, bill history, and metrics.

Customers are introduced by bill creation; this module also supports editing
their profile and surfacing their bill activity.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.crud import bill as bill_crud
from app.crud import customer as customer_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.bill import BillPage, BillRead
from app.schemas.customer import CustomerMetrics, CustomerPage, CustomerRead, CustomerUpdate

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

@router.patch("/{customer_id}", response_model=CustomerRead)
async def update_customer(
    customer_id: int,
    body: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Partially update a customer profile. `code` is immutable."""
    customer = await customer_crud.get_customer(db, customer_id)
    if customer is None:
        raise NotFoundError("CUSTOMER_NOT_FOUND")
    customer = await customer_crud.update_customer(db, customer, body)
    return CustomerRead.model_validate(customer)

@router.get("/{customer_id}/bills", response_model=BillPage)
async def list_customer_bills(
    customer_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    role: str | None = Query(None, pattern="^(all|sender|receiver)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List bills where the customer is sender and/or receiver."""
    if await customer_crud.get_customer(db, customer_id) is None:
        raise NotFoundError("CUSTOMER_NOT_FOUND")
    items, total = await bill_crud.list_bills_by_customer(
        db,
        customer_id=customer_id,
        role=role or "all",
        page=page,
        page_size=page_size,
    )
    return BillPage(
        items=[BillRead.from_model(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )

@router.get("/{customer_id}/metrics", response_model=CustomerMetrics)
async def get_customer_metrics(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return headline metrics for the customer's bill activity."""
    if await customer_crud.get_customer(db, customer_id) is None:
        raise NotFoundError("CUSTOMER_NOT_FOUND")
    return await bill_crud.customer_bill_metrics(db, customer_id)
