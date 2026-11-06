"""Dashboard aggregation CRUD — read-only aggregates over the bills table.

Every query filters on ``bills.created_at`` (naive UTC) and buckets the daily
series by Vietnam local dates. Money sums are returned as ``Decimal``; callers
quantize them before building response schemas.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bill import Bill

_VN_ZONE = "Asia/Ho_Chi_Minh"


def _local_day():
    """SQL expression: a bill's ``created_at`` as a Vietnam-local ``date``."""
    return cast(
        func.timezone(_VN_ZONE, func.timezone("UTC", Bill.created_at)),
        Date,
    ).label("day")


async def fetch_totals(
    db: AsyncSession, start_utc: datetime, end_utc: datetime
) -> dict[str, int | Decimal]:
    """Return the headline aggregates for bills created in the range."""
    stmt = select(
        func.count().label("total_bills"),
        func.count()
        .filter(Bill.status.in_(("created", "picked_up", "in_transit")))
        .label("in_progress_bills"),
        func.count().filter(Bill.status == "delivered").label("delivered_bills"),
        func.count().filter(Bill.status == "cancelled").label("cancelled_bills"),
        func.count().filter(Bill.status == "returned").label("returned_bills"),
        func.coalesce(
            func.sum(Bill.fee_total).filter(Bill.status != "cancelled"), 0
        ).label("revenue_total"),
        func.coalesce(
            func.sum(Bill.cod_amount).filter(Bill.status != "cancelled"), 0
        ).label("cod_total"),
    ).where(Bill.created_at >= start_utc, Bill.created_at < end_utc)

    row = (await db.execute(stmt)).one()
    return {
        "total_bills": row.total_bills,
        "in_progress_bills": row.in_progress_bills,
        "delivered_bills": row.delivered_bills,
        "cancelled_bills": row.cancelled_bills,
        "returned_bills": row.returned_bills,
        "revenue_total": row.revenue_total,
        "cod_total": row.cod_total,
    }


async def fetch_daily(
    db: AsyncSession, start_utc: datetime, end_utc: datetime
) -> list[tuple[date, int, Decimal]]:
    """Return per-day ``(date, bills, revenue)`` rows ordered by date."""
    day = _local_day()
    stmt = (
        select(
            day,
            func.count().label("bills"),
            func.coalesce(
                func.sum(Bill.fee_total).filter(Bill.status != "cancelled"), 0
            ).label("revenue"),
        )
        .where(Bill.created_at >= start_utc, Bill.created_at < end_utc)
        .group_by(day)
        .order_by(day)
    )
    rows = (await db.execute(stmt)).all()
    return [(row.day, row.bills, row.revenue) for row in rows]


async def fetch_status_counts(
    db: AsyncSession, start_utc: datetime, end_utc: datetime
) -> dict[str, int]:
    """Return ``{status: count}`` for bills created in the range."""
    stmt = (
        select(Bill.status, func.count().label("count"))
        .where(Bill.created_at >= start_utc, Bill.created_at < end_utc)
        .group_by(Bill.status)
    )
    rows = (await db.execute(stmt)).all()
    return {row.status: row.count for row in rows}


async def fetch_destinations(
    db: AsyncSession, start_utc: datetime, end_utc: datetime
) -> dict[str, int]:
    """Return ``{province_code: count}`` for bills created in the range.

    Blank or missing ``receiver_snapshot.province_code`` rows are dropped here;
    the service reconciles the result against the canonical province list.
    """
    province_code = Bill.receiver_snapshot["province_code"].astext
    stmt = (
        select(province_code.label("province_code"), func.count().label("count"))
        .where(
            Bill.created_at >= start_utc,
            Bill.created_at < end_utc,
            province_code.isnot(None),
            province_code != "",
        )
        .group_by(province_code)
    )
    rows = (await db.execute(stmt)).all()
    return {row.province_code: row.count for row in rows}
