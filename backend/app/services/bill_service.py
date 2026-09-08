"""Bill business logic — create, validate (aligned to Hoàng Nam DB v1.1)."""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, ConflictError, NotFoundError
from app.crud import audit as audit_crud
from app.crud import bill as bill_crud
from app.crud import customer as customer_crud
from app.models.bill import Bill
from app.models.bill_content_line import BillContentLine
from app.models.service_tier import ServiceTier
from app.schemas.bill import BillCreate, BillParty, BillStatusUpdate, BillUpdate
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
    # Validate service tier exists and is active (optional field)
    if payload.service_tier_code is not None:
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


ALLOWED_TRANSITIONS = {
    "created": {"picked_up", "cancelled"},
    "picked_up": {"in_transit", "returned", "cancelled"},
    "in_transit": {"delivered", "returned"},
    "delivered": set(), "returned": set(), "cancelled": set(),
}


async def transition_status(db: AsyncSession, bill_id: int, payload: BillStatusUpdate, actor_id: int) -> Bill:
    bill = await bill_crud.get_bill(db, bill_id)
    if bill is None:
        raise NotFoundError("BILL_NOT_FOUND")
    if payload.to_status.value not in ALLOWED_TRANSITIONS[bill.status]:
        raise ConflictError("INVALID_STATUS_TRANSITION")
    if payload.to_status.value == "delivered" and not (payload.delivered_to_name or "").strip():
        raise AppError("DELIVERED_TO_NAME_REQUIRED")
    if payload.to_status.value == "cancelled" and not (payload.cancellation_reason or "").strip():
        raise AppError("CANCELLATION_REASON_REQUIRED")
    if payload.to_status.value == "returned" and not (payload.note or "").strip():
        raise AppError("RETURN_REASON_REQUIRED")
    previous = bill.status
    bill.status = payload.to_status.value
    bill.updated_by = actor_id
    if bill.status == "delivered":
        bill.delivered_to_name = payload.delivered_to_name.strip()
        bill.delivered_at = datetime.now(timezone.utc)
    if bill.status == "cancelled":
        bill.cancellation_reason = payload.cancellation_reason.strip()
    if payload.note:
        bill.note = payload.note
    from app.models.bill_status_event import BillStatusLog
    db.add(BillStatusLog(bill_id=bill.id, from_status=previous, to_status=bill.status,
                         note=payload.note, changed_by=actor_id))
    await audit_crud.log_event(db, actor_id=actor_id, action="bill.status_changed",
        entity_type="bill", entity_id=bill.id,
        details={"from_status": previous, "to_status": bill.status, "note": payload.note})
    await db.flush()
    return await bill_crud.get_bill(db, bill.id)


def _snapshot_from_party(party: BillParty, customer_id: int) -> dict:
    return bill_crud.party_snapshot(party, customer_id)


async def update_bill(db: AsyncSession, bill_id: int, payload: BillUpdate, actor_id: int) -> Bill:
    bill = await bill_crud.get_bill(db, bill_id)
    if bill is None:
        raise NotFoundError("BILL_NOT_FOUND")
    if abs((bill.updated_at - payload.expected_updated_at).total_seconds()) > 0.001:
        raise ConflictError("BILL_STALE")
    data = payload.model_dump(exclude_unset=True, exclude={"expected_updated_at", "edit_reason"})
    if not data:
        return bill
    post_pickup = bill.status in {"picked_up", "in_transit"}
    if bill.status in {"delivered", "returned", "cancelled"}:
        raise ConflictError("BILL_LOCKED")
    if post_pickup:
        if not payload.edit_reason:
            raise AppError("EDIT_REASON_REQUIRED")
        allowed = {"receiver", "note"}
        if set(data) - allowed:
            raise ConflictError("BILL_FIELDS_LOCKED")
    changes = {}
    if "sender" in data:
        sender_id = await _resolve_customer(db, payload.sender)
        before, bill.sender_id = bill.sender_snapshot, sender_id
        bill.sender_snapshot = _snapshot_from_party(payload.sender, sender_id)
        changes["sender"] = {"before": before, "after": bill.sender_snapshot}
    if "receiver" in data:
        receiver_id = await _resolve_customer(db, payload.receiver)
        before, bill.receiver_id = bill.receiver_snapshot, receiver_id
        bill.receiver_snapshot = _snapshot_from_party(payload.receiver, receiver_id)
        changes["receiver"] = {"before": before, "after": bill.receiver_snapshot}
    for field in ("cargo_type", "service_tier_code", "actual_weight_kg", "is_insurance_required", "cod_amount", "payer", "note"):
        if field in data and getattr(bill, field) != data[field]:
            before = getattr(bill, field)
            setattr(bill, field, _weight(data[field]) if field == "actual_weight_kg" else (_money(data[field]) if field == "cod_amount" else data[field]))
            changes[field] = {"before": str(before) if before is not None else None, "after": data[field]}
    if "fee" in data:
        for field, value in data["fee"].items():
            before = getattr(bill, field)
            setattr(bill, field, _money(value))
            if before != getattr(bill, field): changes[field] = {"before": str(before), "after": value}
    if "contents" in data:
        bill.content_lines.clear()
        await db.flush()
        for idx, line in enumerate(payload.contents, 1):
            bill.content_lines.append(BillContentLine(
                line_no=idx, cargo_type=line.cargo_type, description=line.description, quantity=line.quantity,
                weight_kg=_weight(line.weight_kg), length_cm=line.length_cm, width_cm=line.width_cm,
                height_cm=line.height_cm, images=line.images, metadata_=line.metadata))
        bill.chargeable_weight_kg = _compute_chargeable_weight(payload.model_copy(update={"contents": payload.contents, "actual_weight_kg": float(bill.actual_weight_kg)}))
        changes["contents"] = {"before": "updated", "after": "updated"}
    bill.updated_by = actor_id
    await audit_crud.log_event(db, actor_id=actor_id, action="bill.updated", entity_type="bill", entity_id=bill.id,
        details={"changes": changes, "reason": payload.edit_reason})
    await db.flush()
    return await bill_crud.get_bill(db, bill.id)
