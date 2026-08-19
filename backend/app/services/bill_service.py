"""Bill business logic — create, validate (aligned to Hoàng Nam DB v1.1)."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, NotFoundError
from app.crud import bill as bill_crud
from app.crud import customer as customer_crud
from app.models.bill import Bill
from app.models.service_tier import ServiceTier
from app.schemas.bill import BillCreate, BillParty
from app.schemas.customer import CustomerCreate

# Dimensional weight divisor (BR-01 / BR-WAY-2.1)
DIM_WEIGHT_DIVISOR = Decimal("6000")


def _compute_chargeable_weight(payload: BillCreate) -> Decimal:
    """chargeable_weight_kg = max(actual_weight_kg, Σ(dài × rộng × cao / 6000))."""
    actual = Decimal(str(payload.actual_weight_kg))
    dim_total = Decimal("0")
    for line in payload.contents:
        if line.length_cm and line.width_cm and line.height_cm:
            volume = (
                Decimal(str(line.length_cm))
                * Decimal(str(line.width_cm))
                * Decimal(str(line.height_cm))
            )
            dim_total += volume / DIM_WEIGHT_DIVISOR
    return max(actual, dim_total)


async def _resolve_customer(db: AsyncSession, party: BillParty) -> int:
    """Return a customer id for a sender/receiver block (get-or-create by phone)."""
    if party.customer_id is not None:
        existing = await customer_crud.get_customer(db, party.customer_id)
        if existing is None:
            raise NotFoundError("CUSTOMER_NOT_FOUND")
        return existing.id

    existing = await customer_crud.get_customer_by_phone(db, party.phone)
    if existing is not None:
        return existing.id

    customer = await customer_crud.create_customer(
        db,
        CustomerCreate(
            name=party.name,
            phone=party.phone,
            customer_type="retail",
            address_detail=party.address_detail,
            province_code=party.province_code,
            province_name=party.province_name,
            ward_code=party.ward_code,
            ward_name=party.ward_name,
        ),
    )
    return customer.id


async def create_bill(
    db: AsyncSession,
    payload: BillCreate,
    actor_id: int,
) -> Bill:
    """Create a bill with full validation (UC-WAYBILL-01 / FR-WAY-02)."""
    # Validate service tier exists and is active
    result = await db.execute(
        select(ServiceTier).where(ServiceTier.code == payload.service_tier_code)
    )
    tier = result.scalar_one_or_none()
    if tier is None or not tier.is_active:
        raise NotFoundError("TIER_NOT_FOUND")

    if not payload.contents:
        raise AppError("CONTENT_LINES_REQUIRED")

    # Resolve sender / receiver customers (get-or-create khách vãng lai)
    sender_id = await _resolve_customer(db, payload.sender)
    receiver_id = await _resolve_customer(db, payload.receiver)

    # Compute chargeable weight
    chargeable_weight_kg = _compute_chargeable_weight(payload)

    return await bill_crud.create_bill(
        db,
        payload=payload,
        actor_id=actor_id,
        sender_id=sender_id,
        receiver_id=receiver_id,
        chargeable_weight_kg=chargeable_weight_kg,
    )
