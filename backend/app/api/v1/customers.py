"""Customers API — lookup by phone and create."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.crud import customer as customer_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerRead

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerRead])
async def list_customers(
    phone: str | None = Query(None, description="Filter by phone number"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List customers, optionally filtered by phone (used for sender/receiver autofill)."""
    if phone:
        customer = await customer_crud.get_customer_by_phone(db, phone)
        return [CustomerRead.model_validate(customer)] if customer else []
    from app.models.customer import Customer
    from sqlalchemy import select

    result = await db.execute(select(Customer).order_by(Customer.name).limit(100))
    return [CustomerRead.model_validate(c) for c in result.scalars().all()]


@router.post("", response_model=CustomerRead, status_code=201)
async def create_customer(
    body: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new customer (khách vãng lai)."""
    customer = await customer_crud.create_customer(db, body)
    await db.commit()
    await db.refresh(customer)
    return CustomerRead.model_validate(customer)
