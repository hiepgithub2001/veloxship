"""Customer business logic — manual create/update, bill history, and metrics.

The API layer stays thin: every rule (not-found handling, audit trail,
duplicate-phone flagging, revenue attribution) lives here.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.crud import audit as audit_crud
from app.crud import bill as bill_crud
from app.crud import customer as customer_crud
from app.models.bill import Bill
from app.models.customer import Customer
from app.schemas.customer import (
    CustomerCreate,
    CustomerMetrics,
    CustomerUpdate,
)


async def list_customers(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[Customer], int]:
    """Return a page of the customer directory."""
    return await customer_crud.list_customers(
        db,
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active,
    )


async def get_customer(db: AsyncSession, customer_id: int) -> Customer:
    """Return a customer or raise `CUSTOMER_NOT_FOUND`."""
    customer = await customer_crud.get_customer(db, customer_id)
    if customer is None:
        raise NotFoundError("CUSTOMER_NOT_FOUND")
    return customer


async def create_customer(
    db: AsyncSession,
    payload: CustomerCreate,
    actor_id: int,
) -> Customer:
    """Create a customer profile and record who created it.

    A duplicated phone number does not block creation — `bill_service` resolves
    customers by phone, so blocking here would break bill entry. The duplicate
    is flagged in the audit details instead.
    """
    duplicate_phone = await customer_crud.phone_exists(db, payload.phone)
    customer = await customer_crud.create_customer(db, payload)
    await audit_crud.log_event(
        db,
        actor_id=actor_id,
        action="customer:create",
        entity_type="customer",
        entity_id=customer.id,
        details={
            "name": customer.name,
            "phone": customer.phone,
            "duplicate_phone": duplicate_phone,
        },
    )
    return customer


async def update_customer(
    db: AsyncSession,
    customer_id: int,
    payload: CustomerUpdate,
    actor_id: int,
) -> Customer:
    """Update a customer profile and record which fields changed."""
    customer = await get_customer(db, customer_id)
    changed_fields = sorted(payload.model_dump(exclude_unset=True).keys())
    customer = await customer_crud.update_customer(db, customer, payload)
    await audit_crud.log_event(
        db,
        actor_id=actor_id,
        action="customer:update",
        entity_type="customer",
        entity_id=customer.id,
        details={"changed_fields": changed_fields},
    )
    return customer


async def list_customer_bills(
    db: AsyncSession,
    customer_id: int,
    *,
    role: str = "all",
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[Bill], int]:
    """Return the customer's bill history, optionally filtered by side."""
    await get_customer(db, customer_id)
    return await bill_crud.list_bills_by_customer(
        db,
        customer_id=customer_id,
        role=role,
        page=page,
        page_size=page_size,
    )


async def get_metrics(db: AsyncSession, customer_id: int) -> CustomerMetrics:
    """Return the customer's headline activity metrics."""
    await get_customer(db, customer_id)
    data = await bill_crud.customer_bill_metrics(db, customer_id)
    return CustomerMetrics(**data)
