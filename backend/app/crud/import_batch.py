"""Import batch / row persistence — queries only, no business rules."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.import_batch import ImportBatch, ImportRow


async def create_batch(
    db: AsyncSession,
    *,
    batch: ImportBatch,
    rows: list[ImportRow],
) -> ImportBatch:
    """Persist a batch together with every validated row."""
    # Assign the collection BEFORE the instance is persisted. On a pending
    # object this is pure in-memory work; doing it after `flush()` would make
    # SQLAlchemy lazy-load the relationship (SELECT) and blow up in an async
    # session with "greenlet_spawn has not been called".
    batch.rows = list(rows)
    db.add(batch)
    await db.flush()
    return batch


async def get_batch(
    db: AsyncSession,
    batch_id: int,
    *,
    with_rows: bool = False,
) -> ImportBatch | None:
    """Load one batch, optionally with its rows."""
    if with_rows:
        from sqlalchemy.orm import selectinload

        query = (
            select(ImportBatch)
            .where(ImportBatch.id == batch_id)
            .options(selectinload(ImportBatch.rows))
        )
    else:
        query = select(ImportBatch).where(ImportBatch.id == batch_id)
    return (await db.execute(query)).scalar_one_or_none()


async def list_batches(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ImportBatch], int]:
    """Return one page of import history, newest first."""
    total = (
        await db.execute(select(func.count()).select_from(ImportBatch))
    ).scalar_one()
    items = (
        (
            await db.execute(
                select(ImportBatch)
                .order_by(ImportBatch.created_at.desc(), ImportBatch.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        .scalars()
        .all()
    )
    return list(items), total


async def list_rows(
    db: AsyncSession,
    batch_id: int,
    *,
    status: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[ImportRow], int]:
    """Return one page of a batch's rows, ordered by spreadsheet row number."""
    base = select(ImportRow).where(ImportRow.batch_id == batch_id)
    count_query = (
        select(func.count())
        .select_from(ImportRow)
        .where(ImportRow.batch_id == batch_id)
    )
    if status:
        base = base.where(ImportRow.status == status)
        count_query = count_query.where(ImportRow.status == status)

    total = (await db.execute(count_query)).scalar_one()
    items = (
        (
            await db.execute(
                base.order_by(ImportRow.row_number)
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        .scalars()
        .all()
    )
    return list(items), total


async def get_rows(
    db: AsyncSession,
    batch_id: int,
    *,
    statuses: tuple[str, ...] | None = None,
) -> list[ImportRow]:
    """Return every row of a batch, optionally filtered by status."""
    query = select(ImportRow).where(ImportRow.batch_id == batch_id)
    if statuses:
        query = query.where(ImportRow.status.in_(statuses))
    query = query.order_by(ImportRow.row_number)
    return list((await db.execute(query)).scalars().all())


async def find_completed_batch_by_hash(
    db: AsyncSession,
    file_hash: str,
) -> ImportBatch | None:
    """Return an earlier successfully imported batch with the same file hash."""
    query = (
        select(ImportBatch)
        .where(
            ImportBatch.file_hash == file_hash,
            ImportBatch.status.in_(("completed", "partially_completed")),
        )
        .order_by(ImportBatch.id.desc())
        .limit(1)
    )
    return (await db.execute(query)).scalar_one_or_none()


async def get_existing_tracking_numbers(
    db: AsyncSession,
    candidates: list[str],
    *,
    chunk_size: int = 500,
) -> set[str]:
    """Return which of the candidate tracking numbers already exist in bills."""
    from app.models.bill import Bill

    existing: set[str] = set()
    for start in range(0, len(candidates), chunk_size):
        chunk = candidates[start : start + chunk_size]
        if not chunk:
            continue
        result = await db.execute(
            select(Bill.tracking_number).where(Bill.tracking_number.in_(chunk))
        )
        existing.update(result.scalars().all())
    return existing


async def get_existing_customer_phones(
    db: AsyncSession,
    candidates: list[str],
    *,
    chunk_size: int = 500,
) -> set[str]:
    """Return which of the candidate phone numbers already belong to a customer."""
    from app.models.customer import Customer

    existing: set[str] = set()
    wanted = [phone for phone in candidates if phone]
    for start in range(0, len(wanted), chunk_size):
        chunk = wanted[start : start + chunk_size]
        if not chunk:
            continue
        result = await db.execute(
            select(Customer.phone).where(Customer.phone.in_(chunk))
        )
        existing.update(result.scalars().all())
    return existing
