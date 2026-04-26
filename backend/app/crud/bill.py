"""Bill CRUD operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import audit as audit_crud
from app.models.bill import Bill
from app.models.bill_content_line import BillContentLine
from app.models.bill_status_event import BillStatusEvent
from app.schemas.bill import BillCreate
from app.services.tracking import next_tracking_number


async def create_bill(
    db: AsyncSession,
    *,
    payload: BillCreate,
    actor_id: int,
) -> Bill:
    """Create a bill with content lines and initial status event in one transaction."""
    tracking = await next_tracking_number(db)

    bill = Bill(
        tracking_number=tracking,
        customer_code=payload.customer_code,
        customer_id=payload.customer_id,
        # Sender snapshot
        sender_name=payload.sender.name,
        sender_address=payload.sender.address,
        sender_district=payload.sender.district,
        sender_province=payload.sender.province,
        sender_phone=payload.sender.phone,
        # Receiver snapshot
        receiver_name=payload.receiver.name,
        receiver_address=payload.receiver.address,
        receiver_district=payload.receiver.district,
        receiver_province=payload.receiver.province,
        receiver_phone=payload.receiver.phone,
        # Service
        cargo_type=payload.cargo_type,
        service_tier_code=payload.service_tier_code,
        # Fees
        fee_main=payload.fee.fee_main,
        fee_fuel_surcharge=payload.fee.fee_fuel_surcharge,
        fee_other_surcharge=payload.fee.fee_other_surcharge,
        fee_vat=payload.fee.fee_vat,
        fee_total=payload.fee.fee_total,
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
            weight_kg=line.weight_kg,
            length_cm=line.length_cm,
            width_cm=line.width_cm,
            height_cm=line.height_cm,
        )
        db.add(content_line)

    # Initial status event
    event = BillStatusEvent(
        bill_id=bill.id,
        from_status=None,
        to_status="da_tao",
        actor_id=actor_id,
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

    # Reload with relationships
    return await get_bill(db, bill.id)


async def get_bill(db: AsyncSession, bill_id: int) -> Bill | None:
    """Get a bill with content lines and status events eager-loaded."""
    result = await db.execute(
        select(Bill)
        .where(Bill.id == bill_id)
        .options(
            selectinload(Bill.content_lines),
            selectinload(Bill.status_events),
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
            selectinload(Bill.status_events),
        )
    )
    return result.scalar_one_or_none()


async def list_bills(db: AsyncSession, page: int = 1, page_size: int = 10) -> tuple[list[Bill], int]:
    """List bills with pagination."""
    from sqlalchemy import func
    
    # Get total count
    count_result = await db.execute(select(func.count(Bill.id)))
    total = count_result.scalar_one()

    # Get items
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Bill)
        .order_by(Bill.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .options(
            selectinload(Bill.content_lines),
            selectinload(Bill.status_events),
        )
    )
    items = list(result.scalars().all())
    
    return items, total
