"""Customers API — directory, manual create/edit, bill history, and metrics.

Customers are still created implicitly when a bill is recorded (khách vãng lai),
but this module also supports managing a profile directly (UC-WEB-13).

Deleting is intentionally NOT exposed: customers are referenced by bills, so
deactivation via `is_active` is the soft-delete path.
"""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.bill import BillPage, BillRead
from app.schemas.customer import (
    CustomerCreate,
    CustomerMetrics,
    CustomerPage,
    CustomerRead,
    CustomerUpdate,
)
from app.services import customer_service

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=CustomerPage)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, min_length=1, max_length=100),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("customer:view")),
):
    """List customer profiles with accent-insensitive search."""
    items, total = await customer_service.list_customers(
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


@router.post("", response_model=CustomerRead, status_code=201)
async def create_customer(
    body: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("customer:create")),
):
    """Create a customer profile manually.

    A duplicated phone number is allowed (the bill flow resolves customers by
    phone and must never be blocked); the duplicate is recorded in the audit
    trail so it stays traceable.
    """
    customer = await customer_service.create_customer(db, body, current_user.id)
    return CustomerRead.model_validate(customer)


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("customer:view")),
):
    """Return one customer profile."""
    customer = await customer_service.get_customer(db, customer_id)
    return CustomerRead.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerRead)
async def update_customer(
    customer_id: int,
    body: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("customer:update")),
):
    """Partially update a customer profile. `code` is immutable."""
    customer = await customer_service.update_customer(db, customer_id, body, current_user.id)
    return CustomerRead.model_validate(customer)


@router.get("/{customer_id}/bills", response_model=BillPage)
async def list_customer_bills(
    customer_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    role: Literal["all", "sender", "receiver"] = Query("all"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("customer:view")),
):
    """List bills where this customer is the sender and/or the receiver."""
    items, total = await customer_service.list_customer_bills(
        db,
        customer_id,
        role=role,
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
    current_user: User = Depends(require_permission("customer:view")),
):
    """Return headline activity metrics for the customer."""
    return await customer_service.get_metrics(db, customer_id)
