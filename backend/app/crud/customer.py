"""Customer CRUD operations."""

from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


async def _next_customer_code(db: AsyncSession) -> str:
    """Generate the next unique customer code from the DB sequence.

    Format: {PREFIX}{seq:06d}  e.g. KH000001
    """
    result = await db.execute(text("SELECT nextval('customer_code_seq')"))
    seq_value = result.scalar_one()
    return f"{settings.CUSTOMER_CODE_PREFIX}{seq_value:06d}"


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
        select(Customer).where(Customer.phone == phone, Customer.is_active.is_(True)).limit(1)
    )
    return result.scalar_one_or_none()


async def list_customers(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[Customer], int]:
    """Return a paginated customer directory with accent-insensitive search."""
    query = select(Customer)

    if search and (search_term := search.strip()):
        escaped_term = search_term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped_term}%"
        normalized_pattern = func.f_unaccent(func.lower(pattern))
        query = query.where(
            or_(
                func.f_unaccent(func.lower(Customer.name)).like(normalized_pattern, escape="\\"),
                func.f_unaccent(func.lower(Customer.code)).like(normalized_pattern, escape="\\"),
                Customer.phone.ilike(pattern, escape="\\"),
            )
        )

    if is_active is not None:
        query = query.where(Customer.is_active.is_(is_active))

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(
        query.order_by(Customer.created_at.desc(), Customer.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return list(result.scalars().all()), total


async def create_customer(db: AsyncSession, payload: CustomerCreate) -> Customer:
    """Create a customer, storing address fields into `metadata`."""
    customer = Customer(
        code=await _next_customer_code(db),
        name=payload.name,
        phone=payload.phone,
        customer_type=payload.customer_type,
        customer_metadata=_build_metadata(payload),
        is_active=True,
    )
    db.add(customer)
    await db.flush()
    return customer

_ADDRESS_FIELDS = (
    "address_detail",
    "province_code",
    "province_name",
    "ward_code",
    "ward_name",
)

async def update_customer(
    db: AsyncSession, customer: Customer, payload: CustomerUpdate,
) -> Customer:
    """Partially update a customer, merging address fields into `metadata`."""
    update_data = payload.model_dump(exclude_unset=True)

    metadata = dict(customer.customer_metadata or {})
    for field in _ADDRESS_FIELDS:
        if field in update_data:
            value = update_data.pop(field)
            if value is None:
                metadata.pop(field, None)
            else:
                metadata[field] = value
    customer.customer_metadata = metadata or None

    for field, value in update_data.items():
        setattr(customer, field, value)

    await db.flush()
    await db.refresh(customer)
    return customer
