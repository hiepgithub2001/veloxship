"""Customer CRUD operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate


def _build_metadata(payload: CustomerCreate) -> dict | None:
    """Merge flattened address fields into the customer metadata JSONB."""
    meta: dict = {}
    if payload.address_detail is not None:
        meta["address_detail"] = payload.address_detail
    if payload.province_code is not None:
        meta["province_code"] = payload.province_code
    if payload.province_name is not None:
        meta["province_name"] = payload.province_name
    if payload.ward_code is not None:
        meta["ward_code"] = payload.ward_code
    if payload.ward_name is not None:
        meta["ward_name"] = payload.ward_name
    return meta or None


async def get_customer(db: AsyncSession, customer_id: int) -> Customer | None:
    """Get a customer by id."""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    return result.scalar_one_or_none()


async def get_customer_by_phone(db: AsyncSession, phone: str) -> Customer | None:
    """Get an active customer by phone number."""
    if not phone:
        return None
    result = await db.execute(
        select(Customer).where(Customer.phone == phone).limit(1)
    )
    return result.scalar_one_or_none()


async def create_customer(db: AsyncSession, payload: CustomerCreate) -> Customer:
    """Create a customer, storing address fields into `metadata`."""
    customer = Customer(
        name=payload.name,
        phone=payload.phone,
        customer_type=payload.customer_type,
        customer_metadata=_build_metadata(payload),
        is_active=True,
    )
    db.add(customer)
    await db.flush()
    return customer
