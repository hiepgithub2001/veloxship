"""Bills API — create, get, print endpoints."""

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.crud import audit as audit_crud
from app.crud import bill as bill_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.bill import BillCreate, BillRead
from app.services import bill_service

router = APIRouter(prefix="/bills", tags=["bills"])


@router.post("", response_model=BillRead, status_code=201)
async def create_bill(
    body: BillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new delivery bill."""
    bill = await bill_service.create_bill(db, body, current_user.id)
    return BillRead.from_model(bill)


@router.get("/{bill_id}", response_model=BillRead)
async def get_bill(
    bill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single bill by ID."""
    bill = await bill_crud.get_bill(db, bill_id)
    if bill is None:
        raise NotFoundError("BILL_NOT_FOUND")
    return BillRead.from_model(bill)


@router.get("/{bill_id}/print")
async def print_bill(
    bill_id: int,
    as_format: str = Query("pdf", alias="as"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Render the bill for printing. Increments print_count."""
    bill = await bill_crud.get_bill(db, bill_id)
    if bill is None:
        raise NotFoundError("BILL_NOT_FOUND")

    # Increment print count
    from datetime import datetime, timezone
    bill.print_count += 1
    bill.last_printed_at = datetime.now(timezone.utc)
    bill.last_printed_by = current_user.id
    await db.flush()

    # Audit event
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="bill.printed",
        entity_type="bill",
        entity_id=bill.id,
        details={"print_count": bill.print_count},
    )

    if as_format == "html":
        from app.services.print_service import render_bill_html
        html_content = render_bill_html(bill)
        return Response(content=html_content, media_type="text/html")
    else:
        from app.services.print_service import render_bill_pdf
        pdf_bytes = render_bill_pdf(bill)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="phieu-gui-{bill.tracking_number}.pdf"'
            },
        )
