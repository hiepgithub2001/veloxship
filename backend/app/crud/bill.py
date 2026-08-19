"""Bill CRUD operations (aligned to Hoàng Nam DB v1.1)."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import audit as audit_crud
from app.models.bill import Bill
from app.models.bill_content_line import BillContentLine
from app.models.bill_status_event import BillStatusLog
from app.schemas.bill import BillCreate
from app.services.tracking import next_tracking_number


def _money(value: float) -> Decimal:
    """Coerce a float money value to a 2-decimal Decimal (avoids float artifacts)."""
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _weight(value: float) -> Decimal:
    """Coerce a float weight value to a 3-decimal Decimal."""
    return Decimal(str(value)).quantize(Decimal("0.001"))


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
            description=line.description,
            quantity=line.quantity,
            weight_kg=_weight(line.weight_kg),
            length_cm=line.length_cm,
            width_cm=line.width_cm,
            height_cm=line.height_cm,
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


async def list_bills(db: AsyncSession, page: int = 1, page_size: int = 10) -> tuple[list[Bill], int]:
    """List bills with pagination."""
    from sqlalchemy import func

    count_result = await db.execute(select(func.count(Bill.id)))
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    result = await db.execute(
        select(Bill)
        .order_by(Bill.created_at.desc())
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
