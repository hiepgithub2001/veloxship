"""Bill CRUD operations (aligned to Hoàng Nam DB v1.1)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from app.crud import audit as audit_crud
from app.models.audit_event import AuditEvent
from app.models.bill import Bill
from app.models.bill_content_line import BillContentLine
from app.models.bill_status_event import BillStatusLog
from app.models.customer import Customer
from app.models.user import User
from app.schemas.bill import BillCreate
from app.services.tracking import next_tracking_number


def _money(value: float) -> Decimal:
    """Coerce a float money value to a 2-decimal Decimal (avoids float artifacts)."""
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _weight(value: float) -> Decimal:
    """Coerce a float weight value to a 3-decimal Decimal."""
    return Decimal(str(value)).quantize(Decimal("0.001"))


def party_snapshot(party, customer_id: int) -> dict:
    """Persist input data, rather than a mutable customer profile, on the bill."""
    return {
        "customer_id": customer_id, "name": party.name, "phone": party.phone,
        "address_detail": party.address_detail, "province_code": party.province_code,
        "province_name": party.province_name, "ward_code": party.ward_code,
        "ward_name": party.ward_name,
    }


async def create_bill(
    db: AsyncSession,
    *,
    payload: BillCreate,
    actor_id: int,
    sender_id: int,
    receiver_id: int,
    chargeable_weight_kg: Decimal,
) -> Bill:
    """Create a bill with content lines and initial status log in one transaction."""
    tracking = await next_tracking_number(db)

    bill = Bill(
        tracking_number=tracking,
        sender_id=sender_id,
        receiver_id=receiver_id,
        sender_snapshot=party_snapshot(payload.sender, sender_id),
        receiver_snapshot=party_snapshot(payload.receiver, receiver_id),
        # Service & cargo
        cargo_type=payload.cargo_type,
        service_tier_code=payload.service_tier_code,
        actual_weight_kg=_weight(payload.actual_weight_kg),
        chargeable_weight_kg=_weight(float(chargeable_weight_kg)),
        is_insurance_required=payload.is_insurance_required,
        cod_amount=_money(payload.cod_amount),
        # Fees
        fee_main=_money(payload.fee.fee_main),
        fee_insurance=_money(payload.fee.fee_insurance),
        fee_other=_money(payload.fee.fee_other),
        fee_vat=_money(payload.fee.fee_vat),
        fee_total=_money(payload.fee.fee_total),
        # Payer
        payer=payload.payer,
        # Note (free-text remark)
        note=payload.note,
        # Audit
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(bill)
    await db.flush()

    # Content lines
    for idx, line in enumerate(payload.contents, start=1):
        content_line = BillContentLine(
            bill_id=bill.id,
            line_no=line.line_no or idx,
            cargo_type=line.cargo_type,
            description=line.description,
            quantity=line.quantity,
            weight_kg=_weight(line.weight_kg),
            length_cm=line.length_cm,
            width_cm=line.width_cm,
            height_cm=line.height_cm,
            images=line.images,
            metadata_=line.metadata,
        )
        db.add(content_line)

    # Initial status log
    event = BillStatusLog(
        bill_id=bill.id,
        from_status=None,
        to_status="created",
        changed_by=actor_id,
    )
    db.add(event)

    # Audit event
    await audit_crud.log_event(
        db,
        actor_id=actor_id,
        action="bill.created",
        entity_type="bill",
        entity_id=bill.id,
        details={"tracking_number": tracking},
    )

    await db.flush()

    return await get_bill(db, bill.id)


async def get_bill(db: AsyncSession, bill_id: int) -> Bill | None:
    """Get a bill with relationships eager-loaded."""
    result = await db.execute(
        select(Bill)
        .where(Bill.id == bill_id)
        .options(
            selectinload(Bill.content_lines),
            selectinload(Bill.status_logs),
            selectinload(Bill.sender),
            selectinload(Bill.receiver),
        )
    )
    return result.scalar_one_or_none()


async def get_by_tracking_number(db: AsyncSession, tracking_number: str) -> Bill | None:
    """Look up a bill by tracking number."""
    result = await db.execute(
        select(Bill)
        .where(Bill.tracking_number == tracking_number)
        .options(
            selectinload(Bill.content_lines),
            selectinload(Bill.status_logs),
            selectinload(Bill.sender),
            selectinload(Bill.receiver),
        )
    )
    return result.scalar_one_or_none()


async def list_bills(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    status: str | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
) -> tuple[list[Bill], int]:
    """List bills with optional diacritic-insensitive search and AND filters."""
    from sqlalchemy import func

    sender = aliased(Customer)
    receiver = aliased(Customer)
    base_query = (
        select(Bill)
        .join(sender, Bill.sender_id == sender.id)
        .join(receiver, Bill.receiver_id == receiver.id)
    )

    search_term = search.strip() if search else ""
    if search_term:
        escaped_term = search_term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped_term}%"
        conditions = [
            func.f_unaccent(func.lower(Bill.tracking_number)).like(
                func.f_unaccent(func.lower(pattern)),
                escape="\\",
            ),
            func.f_unaccent(func.lower(sender.name)).like(
                func.f_unaccent(func.lower(pattern)),
                escape="\\",
            ),
            func.f_unaccent(func.lower(receiver.name)).like(
                func.f_unaccent(func.lower(pattern)),
                escape="\\",
            ),
            sender.phone.ilike(pattern, escape="\\"),
            receiver.phone.ilike(pattern, escape="\\"),
        ]
        if search_term.isascii() and search_term.isdecimal():
            bill_id = int(search_term)
            if bill_id <= 9_223_372_036_854_775_807:
                conditions.append(Bill.id == bill_id)
        base_query = base_query.where(or_(*conditions))

    # AND filters
    if status:
        base_query = base_query.where(Bill.status == status)
    if created_from is not None:
        base_query = base_query.where(Bill.created_at >= created_from)
    if created_to is not None:
        base_query = base_query.where(Bill.created_at <= created_to)

    count_result = await db.execute(
        select(func.count()).select_from(base_query.subquery()),
    )
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    result = await db.execute(
        base_query.order_by(Bill.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .options(
            selectinload(Bill.content_lines),
            selectinload(Bill.status_logs),
            selectinload(Bill.sender),
            selectinload(Bill.receiver),
        )
    )
    items = list(result.scalars().unique().all())

    return items, total


async def get_events(db: AsyncSession, bill_id: int) -> dict:
    """Return status and audit events enriched with actor names for the detail UI."""
    status_result = await db.execute(
        select(BillStatusLog, User.full_name).outerjoin(User, User.id == BillStatusLog.changed_by)
        .where(BillStatusLog.bill_id == bill_id).order_by(BillStatusLog.created_at)
    )
    audit_result = await db.execute(
        select(AuditEvent, User.full_name).outerjoin(User, User.id == AuditEvent.actor_id)
        .where(AuditEvent.entity_type == "bill", AuditEvent.entity_id == bill_id)
        .order_by(AuditEvent.created_at)
    )
    return {
        "status_events": [{"id": event.id, "bill_id": event.bill_id, "from_status": event.from_status,
            "to_status": event.to_status, "note": event.note, "changed_by": event.changed_by,
            "actor_name": name, "created_at": event.created_at} for event, name in status_result.all()],
        "audit_events": [{"id": event.id, "action": event.action, "actor_id": event.actor_id,
            "actor_name": name, "details": event.details, "created_at": event.created_at}
            for event, name in audit_result.all()],
    }
